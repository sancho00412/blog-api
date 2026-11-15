from unfold.forms import UserChangeForm as BaseChangeForm
from unfold.forms import UserCreationForm as BaseCreationForm

from apps.auths.models import User


class UserCreationForm(BaseCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class UserChangeForm(BaseChangeForm):
    class Meta:
        model = User
        fields = "__all__"
