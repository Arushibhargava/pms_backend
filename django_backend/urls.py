from django.urls import path
from .views import SignupView,CustomLoginView,TeamDashboardView,AddTeamMemberView,CoordinatorDashboardAPIView,CoordinatorMarksAPIView,UpdateCoordinatorMarksAPIView,MentorDashboardAPIView,MentorTasksAPIView,AddTaskAPIView,AssignedMentorCoordinatorView,SendNotificationView
from .views import NotificationListAPIView,WeeklyProgressUpdateView,WeeklyProgressCreateView,WeeklyProgressListView,ProjectListAPIView,UserInfoAPIView,CProjectListAPIView
from .views import TeamTaskListAPI, TaskFileUploadAPI,MentorTeamsView,MentorWeeklyProgressAPIView,UpdateMentorMarksAPIView,SubmitProjectAPIView,UpdateProjectApprovalAPIView,MentorAllocatedTeamsAPIView
from django.conf import settings
from django.conf.urls.static import static
from .views import Coordinator_SendNotificationView,Fetch_all_user
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('team/assigned-users/', AssignedMentorCoordinatorView.as_view(), name='assigned-users'),

    path('team/dashboard/', TeamDashboardView.as_view(), name='team-dashboard'),
    path('team/member/add/', AddTeamMemberView.as_view(), name='add-team-member'),
    path('coordinator/dashboard/', CoordinatorDashboardAPIView.as_view(), name='coordinator-dashboard-api'),
    path('coordinator/marks/', CoordinatorMarksAPIView.as_view(), name='cmarks-api'),
    path('coordinator/marks/update/<str:team_username>/', UpdateCoordinatorMarksAPIView.as_view(), name='update-marks-api'),
    path('mentor/dashboard/', MentorDashboardAPIView.as_view(), name='mentor-dashboard'),
    path('mentor/tasks/', MentorTasksAPIView.as_view(), name='mentor-tasks'),
    path('mentor/tasks/create/', AddTaskAPIView.as_view(), name='mentor-create-task'),
    path('notifications/send/', SendNotificationView.as_view()),
    path('notifications/coordinator/', NotificationListAPIView.as_view()),
    path('notifications/', NotificationListAPIView.as_view()),
    path('weekly-progress/create/', WeeklyProgressCreateView.as_view(), name='create-progress'), #team
    path('weekly-progress/update/', WeeklyProgressUpdateView.as_view(), name='update-progress'),   #team
    path('weekly-progress/', WeeklyProgressListView.as_view(), name='get-progress'),            #team
    path('team-tasks/', TeamTaskListAPI.as_view(), name='team-task-list'),
    path('team-tasks/upload/<int:task_id>/', TaskFileUploadAPI.as_view(), name='upload-task-file'),
    path('mentor-teams/', MentorTeamsView.as_view(), name='mentor-teams'),
    path('mentor/weekly-progress/', MentorWeeklyProgressAPIView.as_view(), name='mentor-weekly-progress'),
    path('marks/update/mentor/<str:team_username>/', UpdateMentorMarksAPIView.as_view(), name='update_mentor_marks'),
    path('project/submit/', SubmitProjectAPIView.as_view(), name='submit-project'),
    path('project/all/', ProjectListAPIView.as_view(), name='list-projects'),
    path('coordinator/project/approval/<int:project_id>/', UpdateProjectApprovalAPIView.as_view(), name='update_project_approval'),
     path('user-info/<str:username>/', UserInfoAPIView.as_view(), name='user-info'),
     path('coordinator/project/',  CProjectListAPIView.as_view(), name='mmarks-api'),

      path('mentor/marks/', MentorAllocatedTeamsAPIView.as_view(), name='mmarks-api'),
    path('coordinator/fetch_users/',Fetch_all_user.as_view(),name='fetch_users'),
    path('coordinator/sendnotification/',Coordinator_SendNotificationView.as_view(),name="send_notification")
]