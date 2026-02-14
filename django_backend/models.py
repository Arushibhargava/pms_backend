from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('team', 'Team'),
        ('mentor', 'Mentor'),
        ('coordinator', 'Coordinator'),
    )



    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    REQUIRED_FIELDS = ['email', 'phone_number', 'name', 'user_type']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"{self.username} ({self.user_type})"
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class Team(models.Model):
    stu_id = models.CharField(max_length=30, primary_key=True)
    member_name = models.CharField(max_length=30)
    student_class = models.CharField(max_length=20)
    branch = models.CharField(max_length=30)
    semester = models.IntegerField()
    stu_rollno = models.IntegerField()
    phone_no = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits.",
                code="invalid_phone_number"
            )
        ]
    )
    email = models.CharField(max_length=50)

    # ✅ Use username as foreign key
    user = models.ForeignKey(
        User,
        to_field='username',        # <---- Reference by username
        db_column='user_username',  # <---- Column in database will be user_username
        on_delete=models.CASCADE,
        related_name='team'
    )

    class Meta:
        db_table = 'team'

    def __str__(self):
        return self.member_name

from django.conf import settings

class ProjectDetails(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=30)
    description = models.TextField(max_length=200)
    approval = models.CharField(max_length=10, default='pending')
    tech_stack = models.TextField(max_length=100)

    team = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='team_username',
        limit_choices_to={'user_type': 'team'}
    )

    class Meta:
        db_table = 'project_details'

    def __str__(self):
        return self.project_name
    
    
from django.db import models
from django.conf import settings


class GroupDetails(models.Model):
    group_id = models.CharField(max_length=10, primary_key=True)
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='mentor_username',
        limit_choices_to={'user_type': 'mentor'},
        related_name='mentor_groups'
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='coordinator_username',
        limit_choices_to={'user_type': 'coordinator'},
        related_name='coordinator_groups'
    )
    team = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='team_username',
        limit_choices_to={'user_type': 'team'},
        related_name='team_groups'
    )
    project_name = models.CharField(max_length=20)

    class Meta:
        db_table = 'group_details'

    def __str__(self):
        return self.group_id

from django.db import models
from django.conf import settings


class Mteam(models.Model):
    team = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        primary_key=True,
        db_column='team_username',
        limit_choices_to={'user_type': 'team'},
        related_name='mteam_entry'
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        to_field='username',
        db_column='mentor_username',
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'mentor'},
        related_name='mentored_teams'
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        to_field='username',
        db_column='coordinator_username',
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'coordinator'},
        related_name='coordinated_teams'
    )

    class Meta:
        db_table = 'mteam'

    def __str__(self):
        return f"{self.team.username} - {self.mentor.username if self.mentor else 'No Mentor'} - {self.coordinator.username if self.coordinator else 'No Coordinator'}"
    
    
from django.db import models
from django.conf import settings

class Marks(models.Model):
    stu_rollno = models.CharField(max_length=20, primary_key=True)
    marks = models.IntegerField(null=True, blank=True)
    member_name = models.CharField(max_length=30)

    # Student ID reference
    stu_id = models.ForeignKey(
        'Team',  # if you're using TeamMember model, replace with 'TeamMember'
        on_delete=models.CASCADE
    )

    # Coordinator (optional)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        to_field='username',
        db_column='coordinator_username',
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'coordinator'},
        related_name='coordinator_marks'
    )

    # Mentor
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='mentor_username',
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'mentor'},
        related_name='mentor_marks'
    )

    coordinator_marks = models.IntegerField(null=True, blank=True)
    percentage = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'marks'

    def __str__(self):
        return self.stu_rollno


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    doc_title = models.CharField(max_length=20)
    status = models.CharField(max_length=10)
    upload_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    
    # Assigned mentor (filtered by user_type='mentor')
    mentor = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'mentor'}
    )

    class Meta:
        db_table = 'task'

    def __str__(self):
        return self.doc_title

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ttask(models.Model):
    Ttask_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    # Team user submitting the file (user_type='team')
    team_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='team_tasks',
        limit_choices_to={'user_type': 'team'}
    )

    # Redundant but useful for display (team name)
    team_name = models.CharField(max_length=50)

    # Optional mentor (for tracking who assigned — you can remove if redundant)
    mentor_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        limit_choices_to={'user_type': 'mentor'}, related_name='assigned_tasks'
    )

    file_upload = models.FileField(upload_to='uploads/', null=True, blank=True)

    class Meta:
        db_table = 'Ttask'

    def __str__(self):
        return f"{self.team_name} - Task {self.task.doc_title}"

class Notification(models.Model):
    sender = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='sent_notifications'
)
    receiver = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='received_notifications'
)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username}'


from django.db import models
from django.conf import settings


from django.conf import settings
from django.db import models

class WeeklyProgress(models.Model):
    team = models.ForeignKey(
        settings.AUTH_USER_MODEL,            # Custom User model
        on_delete=models.CASCADE,
        to_field='username',                 # Use 'username' instead of default 'id'
        db_column='team_username',           # Actual DB column name
        limit_choices_to={'user_type': 'team'}  # Only allow team users
    )
   
    week_number = models.IntegerField()
    goal_tasks = models.JSONField()           # Example: ["UI", "API", "Docs"]
    completed_tasks = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    progress_percent = models.IntegerField(default=0)
    
    def calculate_progress(self):
        total = len(self.goal_tasks)
        done = len(self.completed_tasks)
        if total == 0:
            return 0
        return int((done / total) * 100)
    def save(self, *args, **kwargs):
        self.progress_percent = self.calculate_progress()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Week {self.week_number} - {self.team} ({self.progress_percent}%)"
