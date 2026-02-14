from rest_framework import serializers
from .models import User,Team
from django.contrib.auth.hashers import make_password
from .models import GroupDetails, ProjectDetails, Mteam
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'name', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(SignupSerializer, self).create(validated_data)

from rest_framework import serializers
from .models import Team

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        
        
    def validate_user(self, value):
        if value.user_type != 'team':
            raise serializers.ValidationError("Only team users can have team members.")
        return value
    
# serializers.py
class ProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDetails
        fields = ['project_id', 'project_name', 'description', 'tech_stack', 'approval', 'team']
        read_only_fields = ['team', 'approval', 'project_id']
        
class GroupDetailsSerializer(serializers.ModelSerializer):
    mentor = SignupSerializer()
    coordinator = SignupSerializer()
    team = SignupSerializer()

    class Meta:
        model = GroupDetails
        fields = '__all__'
class MteamSerializer(serializers.ModelSerializer):
    team = SignupSerializer()
    mentor = SignupSerializer()
    coordinator = SignupSerializer()

    class Meta:
        model = Mteam
        fields = '__all__'

from django.contrib.auth import get_user_model

User = get_user_model()

class GroupCreateSerializer(serializers.ModelSerializer):
    team = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.filter(user_type='team'))
    mentor = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.filter(user_type='mentor'))

    class Meta:
        model = GroupDetails
        fields = ['group_id', 'project_name', 'mentor', 'team']

class TeamDisplaySerializer(serializers.Serializer):
    team_username = serializers.CharField()
    team_name = serializers.CharField()
    team_email = serializers.EmailField()
    project_name = serializers.CharField(allow_blank=True)
    allocated_mentor = serializers.CharField(allow_blank=True)
    group_id = serializers.CharField(allow_blank=True)
    members = serializers.ListField()  # Already serialized, so just accept the list


from .models import Marks
from django.contrib.auth import get_user_model

User = get_user_model()

class MarksSerializer(serializers.ModelSerializer):
    mentor = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.filter(user_type='mentor')
    )
    coordinator = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.filter(user_type='coordinator'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Marks
        fields = '__all__'
        
        
from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    mentor = serializers.SlugRelatedField(
        queryset=User.objects.filter(user_type='mentor'),
        slug_field='username'
    )

    class Meta:
        model = Task
        fields = '__all__'
from rest_framework import serializers
from .models import Ttask, Task
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework import serializers
from .models import Ttask

class TtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ttask
        fields = '__all__'
        extra_kwargs = {
            'mentor_user': {'required': False},  # Make optional if needed
            'team_name': {'required': False},
        }

    def validate(self, data):
        # Add any additional validation here
        return data
from rest_framework import serializers
from .models import Notification

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')  # Add more if needed

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'    
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'user_type']
        
from rest_framework import serializers
from .models import WeeklyProgress
from django.contrib.auth import get_user_model

User = get_user_model()

class WeeklyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyProgress
        fields = '__all__'
        read_only_fields = ['created_at', 'progress_percent']

    def validate_team(self, value):
        if value.user_type != 'team':
            raise serializers.ValidationError("Only team users can submit progress.")
        return value

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'phone_number', 'user_type']



