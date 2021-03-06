from apiflask import APIBlueprint, input, output, abort
from flask import g, current_app
from flask.views import MethodView

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.models import UserType
from labelfun.models.user import User
from labelfun.schemas.user import UserCreateInSchema, UserEditInSchema, \
    UserQueryOutSchema

user_bp = APIBlueprint('user', __name__)


@user_bp.route('', endpoint='users')
class UsersView(MethodView):

    @input(UserCreateInSchema)
    @output(UserQueryOutSchema, 201)
    def post(self, data):
        name = data['name']
        email = data['email']
        password = data['password']
        invitation = data['invitation']

        user_with_same_email = User.query.filter_by(email=email).first()
        if user_with_same_email is not None:
            abort(400, 'DUPLICATED_EMAIL')
        if invitation == current_app.config['INVITATION_CODE']:
            new_user = User(name=name, email=email,
                            password=password, type=UserType.USER)
        elif invitation == current_app.config['INVITATION_CODE_ADMIN']:
            new_user = User(name=name, email=email,
                            password=password, type=UserType.ADMIN)
        else:
            abort(400, '邀请码不存在。')
            return

        db.session.add(new_user)
        db.session.commit()
        return new_user


@user_bp.route('/<int:user_id>', endpoint='user')
class UserView(MethodView):

    @output(UserQueryOutSchema)
    @auth_required()
    def get(self, user_id):
        if g.current_user.id != user_id and g.current_user.type != UserType.ADMIN:
            abort(403)
        if g.current_user.id == user_id:
            return g.current_user

        user = User.query.get(user_id)
        if user is None:
            abort(404)
        return user

    @input(UserEditInSchema)
    @output(UserQueryOutSchema)
    @auth_required()
    def patch(self, user_id, data):
        # non-admin users cannot change info of other users
        if g.current_user.id != user_id and g.current_user.type != UserType.ADMIN:
            abort(403, 'UNAUTHORIZED')

        user = User.query.get(user_id)
        if user is None:
            abort(404)

        name = data.get('name')
        email = data.get('email')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if email is not None and email != '':
            user_with_same_email = User.query.filter_by(email=email).first()
            if user_with_same_email is not None and user_with_same_email.id != user_id:
                abort(400, 'DUPLICATED_EMAIL')

        # non-admin users cannot change info without old_password
        if g.current_user.type != UserType.ADMIN:
            if old_password is None or old_password == '':
                abort(403, 'OLD_PASSWORD_REQUIRED')
            if not user.check_password(old_password):
                abort(403, 'INCORRECT_PASSWORD')

        if name is not None and name != '':
            user.name = name
        if email is not None and email != '':
            user.email = email
        if new_password is not None and new_password != '':
            user.set_password(new_password)

        db.session.commit()
        return user
