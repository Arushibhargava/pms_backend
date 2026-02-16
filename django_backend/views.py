from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from django.core.exceptions import ValidationError
class SignupView(APIView):
    def post(self, request):
        print(request.data)
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        expected_role = request.data.get('user_type')  # From role selection on frontend
        print(username)
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if expected_role and user.user_type != expected_role:
            return Response({"error": f"User is not a {expected_role}"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'user_type': user.user_type,
        }, status=status.HTTP_200_OK)

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Team
from .serializers import TeamMemberSerializer

class TeamDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user.username)
        # Ensure only team users can access this
        if user.user_type != 'team':
            return Response({'error': 'Access denied. Only teams can view this dashboard.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Filter members related to the team (based on username as FK)
        members = Team.objects.filter(user=user.username)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddTeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        if user.user_type != 'team':
            return Response({"error": "Only team users can add members."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        print(data)
        data['user'] = user.username  # attach logged-in user to the team member
        print(user.id)
        serializer = TeamMemberSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import GroupDetails, Mteam, ProjectDetails
from .serializers import GroupDetailsSerializer, ProjectDetailsSerializer, GroupCreateSerializer, MteamSerializer
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import User, GroupDetails, ProjectDetails, Mteam
from .serializers import TeamDisplaySerializer, GroupCreateSerializer
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, Team, ProjectDetails, GroupDetails, Mteam
from .serializers import TeamMemberSerializer, TeamDisplaySerializer, GroupCreateSerializer


class CoordinatorDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.user_type != 'coordinator':
            return Response({'detail': 'Only coordinators can access this endpoint'}, 
                          status=status.HTTP_403_FORBIDDEN)

        teams = User.objects.filter(user_type='team')
        serialized_teams = []

        for team in teams:
            members = Team.objects.filter(user=team.username)
            members_serialized = TeamMemberSerializer(members, many=True).data

            project = ProjectDetails.objects.filter(team=team.username).first()
            group = GroupDetails.objects.filter(team=team.username).first()

            # Prepare mentor data - use empty string if no mentor
            mentor_username = ''
            if group and group.mentor:
                mentor_username = group.mentor

            serialized_teams.append({
                'team_username': team.username,
                'team_name': team.name,
                'team_email': team.email,
                'project_name': project.project_name if project else '',
                'allocated_mentor': mentor_username,  # Just the username string
                'group_id': group.group_id if group else '',
                'members': members_serialized
            })

        mentors = User.objects.filter(user_type='mentor').values('id', 'email', 'name', 'username')
        
        # Serialize with TeamDisplaySerializer
        team_data = TeamDisplaySerializer(serialized_teams, many=True).data


        return Response({
            "teams": team_data,
            "mentors": list(mentors)
        })
    def post(self, request):
        if request.user.user_type != 'coordinator':
            return Response({'detail': 'Only coordinators can perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = GroupCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                # Create or update GroupDetails
                GroupDetails.objects.update_or_create(
                    team=data['team'],
                    defaults={
                        'group_id': data['group_id'],
                        'project_name': data['project_name'],
                        'mentor': data['mentor'],
                        'coordinator': request.user
                    }
                )

                # Create or update Mteam
                mteam, created = Mteam.objects.get_or_create(team=data['team'])
                mteam.mentor = data['mentor']
                mteam.coordinator = request.user
                mteam.save()

                return Response({"message": "Group and mentor assigned successfully"}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Team,  Marks
from .serializers import MarksSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
# marks/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Marks
from .models import Team
from .serializers import MarksSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CoordinatorMarksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'coordinator':
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        teams = User.objects.filter(user_type='team')  # ✅ Get all team USERS
        response_data = []

        for team_user in teams:
            team_members = Team.objects.filter(user=team_user.username)  # ✅ Get team members of that team
            members_data = []

            for member in team_members:
                marks_entry = Marks.objects.filter(stu_id=member).first()
                members_data.append({
                    "stu_rollno": member.stu_id,
                    "name": member.member_name,
                    "email": member.email,
                    "mentor_marks": marks_entry.marks if marks_entry else "",
                    "coordinator_marks": marks_entry.coordinator_marks if marks_entry else "",
                    "percentage": marks_entry.percentage if marks_entry else "",
                    "grade": marks_entry.grade if marks_entry else "",
                })

            response_data.append({
                "team_username": team_user.username,
                "team_name": team_user.name,
                "members": members_data
            })

        return Response({"teams": response_data}, status=status.HTTP_200_OK)
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import User, Team, Marks, Mteam
class MentorAllocatedTeamsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ Step 1: Check mentor permission
        if request.user.user_type != 'mentor':
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        mentor = request.user  # This is a User instance

        # ✅ Step 2: Get teams allocated to this mentor from Mteam
        mteams = Mteam.objects.filter(mentor=mentor)
        response_data = []

        for mteam_entry in mteams:
            team_user = mteam_entry.team  # This is a User object (user_type = 'team')

            # ✅ Step 3: Get team members from Team model using the user object
            team_members = Team.objects.filter(user=team_user)
            members_data = []

            for member in team_members:
                marks_entry = Marks.objects.filter(stu_id=member).first()
                members_data.append({
                    "stu_rollno": member.stu_id,
                    "name": member.member_name,
                    "email": member.email,
                    "mentor_marks": marks_entry.marks if marks_entry else "",
                    "coordinator_marks": marks_entry.coordinator_marks if marks_entry else "",
                    "percentage": marks_entry.percentage if marks_entry else "",
                    "grade": marks_entry.grade if marks_entry else "",
                })

            # ✅ Step 4: Add full team data to response
            response_data.append({
                "team_username": team_user.username,
                "team_name": team_user.name,
                "members": members_data
            })

        return Response({"teams": response_data}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Marks, Team
from .serializers import MarksSerializer

class UpdateCoordinatorMarksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_username):
        if request.user.user_type != 'coordinator':
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        team_members = Team.objects.filter(user=team_username)

        for member in team_members:
            key = f"coordinator_marks_{member.stu_id}"
            if key in request.data:
                try:
                    coordinator_marks = int(request.data[key])

                    marks_entry = Marks.objects.filter(stu_id=member).first()

                    if not marks_entry:
                     
                        mentor = None
                        try:
                            mentor = Mteam.objects.get(team=team_username).mentor
                        except Mteam.DoesNotExist:
                            pass

                        marks_entry = Marks(
                            stu_id=member,
                            coordinator=request.user,
                            coordinator_marks=coordinator_marks,
                            stu_rollno=member.stu_rollno,
                            member_name=member.member_name,
                            mentor=mentor
                        )
                    else:
                        marks_entry.coordinator = request.user
                        marks_entry.coordinator_marks = coordinator_marks
                        marks_entry.stu_rollno = member.stu_rollno or marks_entry.stu_rollno
                        marks_entry.member_name = member.member_name or marks_entry.member_name

                    # Calculate percentage/grade if mentor marks exist
                    if marks_entry.marks is not None:
                        total = marks_entry.marks + coordinator_marks
                        marks_entry.percentage = total / 2
                        marks_entry.grade = (
                            "A+" if total >= 90 else
                            "A" if total >= 80 else
                            "B" if total >= 70 else
                            "C" if total >= 60 else
                            "D" if total >= 50 else "F"
                        )

                    marks_entry.save()

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Coordinator marks updated successfully."}, status=status.HTTP_200_OK)

class UpdateMentorMarksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_username):
        if request.user.user_type != 'mentor':
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        team_members = Team.objects.filter(user=team_username)

        for member in team_members:
            key = f"mentor_marks_{member.stu_id}"
            if key in request.data:
                try:
                    mentor_marks = int(request.data[key])

                    # Check if a marks entry already exists
                    marks_entry = Marks.objects.filter(stu_id=member).first()

                    if not marks_entry:
                        marks_entry = Marks(
                            stu_id=member,
                            mentor=request.user,
                            marks=mentor_marks,
                            stu_rollno=member.stu_rollno,
                            member_name=member.member_name,
                        )
                    else:
                        marks_entry.mentor = request.user
                        marks_entry.marks = mentor_marks
                        marks_entry.stu_rollno = member.stu_rollno or marks_entry.stu_rollno
                        marks_entry.member_name = member.member_name or marks_entry.member_name

                    # Calculate percentage/grade if coordinator marks exist
                    if marks_entry.coordinator_marks is not None:
                        total = marks_entry.coordinator_marks + mentor_marks
                        marks_entry.percentage = total / 2
                        marks_entry.grade = (
                            "A+" if total >= 90 else
                            "A" if total >= 80 else
                            "B" if total >= 70 else
                            "C" if total >= 60 else
                            "D" if total >= 50 else "F"
                        )

                    marks_entry.save()

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Mentor marks updated successfully."}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Team, Mteam

User = get_user_model()

class MentorDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'mentor':
            return Response({'detail': 'Only mentors can access this endpoint.'}, status=status.HTTP_403_FORBIDDEN)

        mentor_user = request.user

        try:
            assigned_teams = Mteam.objects.filter(mentor=mentor_user)

            team_details = []

            for assignment in assigned_teams:
                team_user = assignment.team

                members = Team.objects.filter(user=team_user.username)

                # ✅ Fetch project details
                project = ProjectDetails.objects.filter(team=team_user).first()
                project_data = {
                    'project_name': project.project_name if project else '',
                    'description': project.description if project else '',
                    'tech_stack': project.tech_stack if project else '',
                    'approval': project.approval if project else 'pending',
                }

                member_data = [
                    {
                        'sno': idx + 1,
                        'name': member.member_name,
                        'class': member.student_class,
                        'branch': member.branch,
                        'stu_id': member.stu_id,
                        'email': member.email,
                        'phone_no': member.phone_no,
                        'semester': member.semester,
                        'roll_no': member.stu_rollno
                    }
                    for idx, member in enumerate(members)
                ]

                team_details.append({
                    'team_username': team_user.username,
                    'team_name': team_user.name,
                    'team_id': team_user.id,
                    'project': project_data,
                    'members': member_data
                })

            return Response({
                'mentor_username': mentor_user.username,
                'mentor_name': mentor_user.name,
                'team_details': team_details
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Task, Ttask
from .serializers import TaskSerializer, TtaskSerializer

class MentorTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user is a mentor
        if request.user.user_type != 'mentor':
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        # Get all tasks created by the mentor
        tasks = Task.objects.filter(mentor=request.user)

        # Build structured response
        data = []
        for task in tasks:
            task_data = TaskSerializer(task).data
            submissions = Ttask.objects.filter(task=task)
            submission_data = TtaskSerializer(submissions, many=True).data
            task_data["submissions"] = submission_data
            data.append(task_data)

        return Response({"tasks": data}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class AddTaskAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if request.user.user_type != 'mentor':
            return Response({"detail": "Only mentors can create tasks."}, status=status.HTTP_403_FORBIDDEN)

        data = {
            "doc_title": request.data.get('document-title'),
            "status": "Pending",
            "start_date": request.data.get('start-date'),
            "end_date": request.data.get('end-date'),
            "description": request.data.get('description', ''),
            "mentor": request.user.username,
            "upload_file": request.FILES.get('file-upload')
        }

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task created successfully!", "task": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()


class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sender = request.user
            receiver_username = request.data.get('receiver')
            message = request.data.get('message')

            print("Sender:", sender)
            print("Receiver Username:", receiver_username)
            print("Message:", message)

            if not receiver_username or not message:
                return Response({"error": "Missing data"}, status=400)

            # Save notification to DB
            receiver = User.objects.get(username=receiver_username)
            Notification.objects.create(sender=sender, receiver=receiver, message=message)

            # Send over WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{receiver_username}',
                {
                    'type': 'send_notification',
                    'message': message,
                    'sender': sender.username
                }
            )

            return Response({"status": "sent"}, status=201)

        except Exception as e:
            print("🚨 Notification Error:", str(e))  # Print the actual error
            return Response({"error": str(e)}, status=500)
from .serializers import UserSerializer
class AssignedMentorCoordinatorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            mteam_entry = Mteam.objects.get(team=user.username)
        except Mteam.DoesNotExist:
            return Response({"error": "No mentor/coordinator assigned."}, status=404)

        mentor = mteam_entry.mentor
        coordinator = mteam_entry.coordinator

        data = {
            "mentor": UserSerializer(mentor).data if mentor else None,
            "coordinator": UserSerializer(coordinator).data if coordinator else None,
        }
        print(data)
        return Response(data)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    print("his has been called")
    def get(self, request):
        # Check if the user is a coordinator
        print("User:", request.user)
        print("Is authenticated:", request.user.is_authenticated)
       
        # Get all notifications for this coordinator user
        notifications = Notification.objects.filter(receiver=request.user).order_by('-timestamp')

        # Serialize and return
        serialized_data = NotificationSerializer(notifications, many=True).data

        return Response({"notifications": serialized_data}, status=status.HTTP_200_OK)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import WeeklyProgress
from .serializers import WeeklyProgressSerializer

class WeeklyProgressCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.user_type != 'team':
            return Response({"detail": "Only team users can submit progress."}, status=403)

        week_number = request.data.get("week_number")
        goal_tasks = request.data.get("goal_tasks")

        if WeeklyProgress.objects.filter(team=user, week_number=week_number).exists():
            return Response({"detail": "This week has already been submitted."}, status=400)

        progress = WeeklyProgress.objects.create(
            team=user,
            week_number=week_number,
            goal_tasks=goal_tasks,
            completed_tasks=[]
        )
        serializer = WeeklyProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WeeklyProgressUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        if user.user_type != 'team':
            return Response({"detail": "Only team users can update progress."}, status=403)

        week_number = request.data.get("week_number")
        completed_tasks = request.data.get("completed_tasks")

        try:
            progress = WeeklyProgress.objects.get(team=user, week_number=week_number)
        except WeeklyProgress.DoesNotExist:
            return Response({"detail": "Progress for this week not found."}, status=404)

        progress.completed_tasks = completed_tasks
        progress.progress_percent = progress.calculate_progress()
        progress.save()

        serializer = WeeklyProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import WeeklyProgress
from .serializers import WeeklyProgressSerializer

class WeeklyProgressListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != 'team':
            return Response({"detail": "Only team users can view their progress."}, status=403)

        progress_entries = WeeklyProgress.objects.filter(team=user).order_by('week_number')
        serializer = WeeklyProgressSerializer(progress_entries, many=True)
        return Response(serializer.data, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Task, Ttask, Mteam
from .serializers import TtaskSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status

class TaskFileUploadAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]  # Both parsers needed
    print("iam working")
    def post(self, request, task_id):
        try:
            print("\n=== Incoming Request Data ===")
            print("Files:", request.FILES)  # Debug what files are received
            print("Data:", request.data)    # Debug other form data
            
            # 1. Get required objects
            user = request.user
            task = get_object_or_404(Task, pk=task_id)
            
            # 2. Verify user is a team member
            if user.user_type != 'team':
                return Response(
                    {'error': 'Only team users can upload files'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 3. Get mentor from Mteam
            try:
                team_relation = Mteam.objects.get(team=user.username)
                mentor = team_relation.mentor
            except Mteam.DoesNotExist:
                return Response(
                    {'error': 'No mentor assigned to this team'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Validate file exists (check both possible field names)
            file = request.FILES.get('file_upload')
            if not file:
                return Response(
                    {'error': 'No file provided. Please use "file" or "file_upload" as field name'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 5. Create and save submission
            
            submission = Ttask.objects.create(
    task=task,
    team_user=user,                # ✅ Must be a User instance
    team_name=user.name,
    mentor_user=mentor,           # ✅ Also must be a User instance
    file_upload=file
)
            
            return Response(
                {
                    'success': True,
                    'message': 'File uploaded successfully',
                    'file_url': submission.file_upload.url
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print("Error:", str(e))  # Debug any exceptions
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class TeamTaskListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user  # Logged-in user

        if user.user_type != 'team':
            return Response({'detail': 'Only teams can access this.'}, status=403)

        try:
            # You stored username in Mteam.team FK, so look up by username
            mapping = Mteam.objects.get(team=user.username)
        except Mteam.DoesNotExist:
            return Response({'detail': 'No mentor assigned to this team.'}, status=404)

        # mentor is a User object due to FK, so we can use it directly
        mentor_user = mapping.mentor

        if not mentor_user:
            return Response({'detail': 'This team has no assigned mentor.'}, status=404)

        # ✅ Finally fetch tasks assigned to that mentor
        tasks = Task.objects.filter(mentor=mentor_user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Mteam
from .serializers import MteamSerializer

class MentorTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type != 'mentor':
            return Response({"detail": "Not authorized."}, status=403)

        teams = Mteam.objects.filter(mentor=user)
        serializer = MteamSerializer(teams, many=True)
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Mteam, WeeklyProgress
from .serializers import WeeklyProgressSerializer

class MentorWeeklyProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ✅ Only mentors are allowed
        if user.user_type != 'mentor':
            return Response({"detail": "Only mentors can access this data."}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Get all teams assigned to this mentor
        team_usernames = Mteam.objects.filter(mentor=user).values_list('team__username', flat=True)

        # ✅ Fetch weekly progress entries for those teams
        progress_data = WeeklyProgress.objects.filter(team__username__in=team_usernames).order_by('week_number')

        # ✅ Serialize
        serializer = WeeklyProgressSerializer(progress_data, many=True)
        return Response({"progress_reports": serializer.data}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ProjectDetails
from .serializers import ProjectDetailsSerializer

class SubmitProjectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(team=request.user)  # Automatically set team from JWT
            return Response({"message": "Project submitted successfully.", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProjectDetails
from .serializers import ProjectDetailsSerializer

class ProjectListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get projects where team == logged in user
        projects = ProjectDetails.objects.filter(team=request.user)
        serializer = ProjectDetailsSerializer(projects, many=True)
        return Response({"projects": serializer.data}, status=200)
    

class CProjectListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get projects where team == logged in user
        projects = ProjectDetails.objects.filter()
        serializer = ProjectDetailsSerializer(projects, many=True)
        return Response(serializer.data, status=200)

class UpdateProjectApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        if request.user.user_type != 'coordinator':
            return Response({"detail": "Unauthorized. Only coordinators can update approval status."}, status=403)

        new_status = request.data.get('approval')
        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status. Choose 'approved' or 'rejected'."}, status=400)

        try:
            project = ProjectDetails.objects.get(project_id=project_id)
            project.approval = new_status
            project.save()
            return Response({"message": f"Project '{project.project_name}' updated to '{new_status}'."}, status=200)
        except ProjectDetails.DoesNotExist:
            return Response({"error": "Project not found."}, status=404)
        
from .serializers import UserInfoSerializer
from rest_framework import status

class UserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            serializer = UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class Fetch_all_user(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_type = request.GET.get("user_type")

            if user_type != 'coordinator':
                return Response(
                    {"error": "You cannot access users"},
                    status=status.HTTP_403_FORBIDDEN
                )

            teams = User.objects.filter(user_type='team')
            mentors = User.objects.filter(user_type='mentor')

            team_serializer = UserSerializer(teams, many=True)
            mentor_serializer = UserSerializer(mentors, many=True)

            return Response({
                "teams": team_serializer.data,
                "mentors": mentor_serializer.data
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class Coordinator_SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sender = request.user
            target = request.data.get('target')
            receiver_username = request.data.get('receiver')
            message = request.data.get('message')

            print("Sender:", sender)
            print("Target:", target)
            print("Receiver:", receiver_username)
            print("Message:", message)

            if not message:
                return Response({"error": "Message is required"}, status=400)

            # ✅ Decide receivers
            if target == "all_teams":
                receivers = User.objects.filter(user_type='team')

            elif target == "all_mentors":
                receivers = User.objects.filter(user_type='mentor')

            elif target == "single":
                if not receiver_username:
                    return Response({"error": "Receiver required"}, status=400)

                receivers = User.objects.filter(username=receiver_username)

            else:
                return Response({"error": "Invalid target"}, status=400)

            # ✅ Create notifications
            notifications = []
            for receiver in receivers:
                notifications.append(
                    Notification(sender=sender, receiver=receiver, message=message)
                )

            Notification.objects.bulk_create(notifications)

            # ✅ Send WebSocket notifications
            channel_layer = get_channel_layer()

            for receiver in receivers:
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{receiver.username}',
                    {
                        'type': 'send_notification',
                        'message': message,
                        'sender': sender.username
                    }
                )

            return Response({"status": "sent"}, status=201)

        except Exception as e:
            print("🚨 Notification Error:", str(e))
            return Response({"error": str(e)}, status=500)
