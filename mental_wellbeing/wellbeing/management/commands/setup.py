from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create Initial Data for setup"
    
    def handle(self, *args, **options):
        try:
            from django.contrib.auth.models import User,Group
            from wellbeing.models import Quiz,Question, Option, TempRecommendation
            from datetime import date
            # User Group Creation
            doctor_group,_ =Group.objects.get_or_create(name="Doctors")
            admin_group,_ =Group.objects.get_or_create(name="Admins")
            # Creating users
            # Creating a Superuser
            superuser, created = User.objects.get_or_create(
                username="superuser",
                defaults={
                    "email": "superuser@example.com",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                }
            )
            if created:
                superuser.set_password("password123")  # Set a secure password
                superuser.save()
                self.stdout.write(self.style.SUCCESS('Superuser created.'))
            else:
                self.stdout.write(self.style.WARNING('Superuser already exists.'))
            
            # Creating an Admin User
            admin_user, created = User.objects.get_or_create(
                username="admin_user",
                defaults={
                    "email": "admin@example.com",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                }
            )
            if created:
                admin_user.set_password("password123")  # Set a secure password
                admin_user.save()
                admin_user.groups.add(admin_group)      
                self.stdout.write(self.style.SUCCESS('Admin user created.'))
            else:
                self.stdout.write(self.style.WARNING('Admin user already exists.'))
            
            # Creating a Doctor User
            doctor_user, created = User.objects.get_or_create(
                username="doctor_user",
                defaults={
                    "email": "doctor@example.com",
                }
            )
            if created:
                doctor_user.set_password("password123")  # Set a secure password
                doctor_user.save()
                doctor_user.groups.add(doctor_group)
                self.stdout.write(self.style.SUCCESS('Doctor user created.'))
            else:
                self.stdout.write(self.style.WARNING('Doctor user already exists.'))              
            # Create Dummy Quiz before hand with some valid recommendations
            quiz, created = Quiz.objects.get_or_create(
            title='Mental Wellness Quiz',
            active_from=date(2024, 12, 22)  # Set an active date for the quiz
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Quiz "{quiz.title}" created successfully.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Quiz "{quiz.title}" already exists.'))

            # Create questions for the quiz
            questions_data = [
                {'text': 'How often do you feel anxious?', 'options': [
                    {'text': 'Never', 'rating': 1},
                    {'text': 'Rarely', 'rating': 2},
                    {'text': 'Sometimes', 'rating': 4},
                    {'text': 'Often', 'rating': 6},
                ]},
                {'text': 'Do you have trouble sleeping?', 'options': [
                    {'text': 'Never', 'rating': 1},
                    {'text': 'Rarely', 'rating': 2},
                    {'text': 'Sometimes', 'rating': 4},
                    {'text': 'Often', 'rating': 6},
                ]},
                {'text': 'Do you feel fatigued during the day?', 'options': [
                    {'text': 'Never', 'rating': 1},
                    {'text': 'Rarely', 'rating': 2},
                    {'text': 'Sometimes', 'rating': 4},
                    {'text': 'Often', 'rating': 6},
                ]},
                {'text': 'How often do you experience feelings of sadness?', 'options': [
                    {'text': 'Never', 'rating': 1},
                    {'text': 'Rarely', 'rating': 2},
                    {'text': 'Sometimes', 'rating': 4},
                    {'text': 'Often', 'rating': 6},
                ]},
                {'text': 'Do you often feel overwhelmed by daily tasks?', 'options': [
                    {'text': 'Never', 'rating': 1},
                    {'text': 'Rarely', 'rating': 2},
                    {'text': 'Sometimes', 'rating': 4},
                    {'text': 'Often', 'rating': 6},
                ]},
                {'text': 'How much support do you feel from your social circle?', 'options': [
                    {'text': 'None', 'rating': 1},
                    {'text': 'A little', 'rating': 2},
                    {'text': 'Moderate', 'rating': 4},
                    {'text': 'Strong', 'rating': 6},
                ]},
                {'text': 'How do you generally handle stress?', 'options': [
                    {'text': 'Ignore it', 'rating': 1},
                    {'text': 'Talk to others', 'rating': 2},
                    {'text': 'Engage in activities', 'rating': 4},
                    {'text': 'Practice mindfulness', 'rating': 6},
                ]},
            ]

            for question_data in questions_data:
                # Create each question related to the quiz
                question, _ = Question.objects.get_or_create(quiz=quiz, text=question_data['text'])
                self.stdout.write(self.style.SUCCESS(f'Question "{question.text}" created successfully.'))

                # Create options for each question
                for option_data in question_data['options']:
                    Option.objects.get_or_create(
                        question=question,
                        text=option_data['text'],
                        rating=option_data['rating']
                    )
                    self.stdout.write(self.style.SUCCESS(f'Option "{option_data["text"]}" created for question "{question.text}".'))

            # Create recommendations based on score ranges
            recommendations_data = [
                {'min_score': 0, 'max_score': 10, 'text': 'You might be experiencing mild symptoms of stress. Consider relaxation techniques like breathing exercises, meditation, or light physical activity.'},
                {'min_score': 11, 'max_score': 20, 'text': 'You may be feeling moderate levels of stress or anxiety. It is important to reach out to your support network, take breaks, and engage in stress-relieving activities.'},
                {'min_score': 21, 'max_score': 30, 'text': 'You could be dealing with significant stress. Please consider seeking professional help, such as talking to a counselor or therapist, to address these feelings.'},
                {'min_score': 31, 'max_score': 42, 'text': 'You may be experiencing high levels of stress or anxiety. We recommend consulting a mental health professional for guidance and support to manage these symptoms effectively.'},
            ]

            for recommendation_data in recommendations_data:
                recommendation, created = TempRecommendation.objects.get_or_create(
                    quiz=quiz,
                    min_score=recommendation_data['min_score'],
                    max_score=recommendation_data['max_score'],
                    text=recommendation_data['text']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Recommendation for score range {recommendation_data["min_score"]}-{recommendation_data["max_score"]} created successfully.'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Recommendation for score range {recommendation_data["min_score"]}-{recommendation_data["max_score"]} already exists.'))
        except Exception as e:
            raise CommandError('Setup failed due to an exception "%s"' % e)
        