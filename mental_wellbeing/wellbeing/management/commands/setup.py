from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create Initial Data for setup"
    
    def handle(self, *args, **options):
        try:
            from django.contrib.auth.models import User,Group
            from wellbeing.models import Quiz,Question, Option, TempRecommendation, MentalWellbeingContent
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
            
            # Create Wellbeing content
            MentalWellbeingContent.objects.get_or_create(
                title="A Comprehensive Analysis of Mental Health Problems in India",
                description="This review article provides a comprehensive overview of the current state of mental health in India, highlighting the challenges faced, existing initiatives, and future directions for improving mental healthcare delivery.",
                content_type="article",
                url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10460242/"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Mental Health in India—Bridging the Gap",
                description="This research paper examines the mental health crisis in India, emphasizing the need for policy reforms and improved mental health services.",
                content_type="article",
                url="https://academic.oup.com/jpubhealth/article/43/Supplement_2/ii2/6383621"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="World Mental Health Day: 60-70 Million People in India Suffer from Common Mental Disorders",
                description="This article highlights the alarming statistics of mental health disorders in India and the barriers to timely treatment.",
                content_type="article",
                url="https://m.economictimes.com/magazines/panache/world-mental-health-day-60-70-mn-people-in-india-suffer-from-common-mental-disorders-stigmatisation-financial-barriers-prevent-timely-treatment/articleshow/104289268.cms"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="An Overview of the Mental Health Crisis with COVID-19 in India",
                description="This article discusses the impact of the COVID-19 pandemic on mental health in India, including increased anxiety and depression.",
                content_type="article",
                url="https://projects.iq.harvard.edu/aia/news/overview-mental-health-crisis-covid-19-india"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Studying Differential Mental Health Expressions in India",
                description="This study analyzes mental health discussions on social media in India, highlighting cultural differences in expressing mental health issues.",
                content_type="article",
                url="https://arxiv.org/abs/2402.11477"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Predicting Suicidal Behavior Among Indian Adults Using Childhood Trauma",
                description="This research paper explores the use of machine learning to predict suicidal behavior in Indian adults based on childhood trauma and mental health questionnaires.",
                content_type="article",
                url="https://arxiv.org/abs/2401.17705"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Psychologs: A Mental Health Magazine in India",
                description="Psychologs is a monthly mental health magazine in India, providing articles, interviews, and columns on various mental health topics.",
                content_type="article",
                url="https://en.wikipedia.org/wiki/Psychologs"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Ayurvedic Self-Care Practices to Cultivate Inner Strength and Peace",
                description="This article discusses Ayurvedic self-care practices such as tongue scraping, oil pulling, and abhyanga to detoxify the body and promote mental well-being.",
                content_type="article",
                url="https://timesofindia.indiatimes.com/life-style/health-fitness/health-news/ayurvedic-self-care-practices-to-cultivate-inner-strength-and-peace/articleshow/110941302.cms"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Winter Wellness: Self-Care Tips for Mind and Body",
                description="This article provides self-care tips for the winter season, including boosting immunity and maintaining physical activity.",
                content_type="article",
                url="https://timesofindia.indiatimes.com/life-style/health-fitness/health-news/winter-wellness-self-care-tips-for-mind-and-body/articleshow/116679136.cms"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Self-care for Mental Health: Practical Tips for a Happier Life",
                description="This article provides practical self-care tips to boost mental well-being, including mindfulness and meditation.",
                content_type="self_care_tip",
                url="https://www.hindustantimes.com/lifestyle/relationships/selfcare-for-mental-health-practical-tips-for-a-happier-life-101704285969318.html"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Mindfulness Techniques for Stress Relief",
                description="This article discusses mindfulness techniques that help reduce stress and improve focus.",
                content_type="self_care_tip",
                url="https://www.deccanherald.com/metrolife/metrolife-your-bond-with-bengaluru/mindfulness-techniques-for-stress-relief-937578.html"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Yoga for Stress Relief | Beginner-Friendly Session",
                description="This YouTube video introduces basic yoga postures designed to relieve stress and improve mental clarity.",
                content_type="video",
                video_url="https://www.youtube.com/embed/8R2FfRl6V8U",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Breathing Exercises to Calm Your Mind",
                description="A guided breathing exercise video to reduce stress and anxiety in just a few minutes.",
                content_type="video",
                video_url="https://www.youtube.com/embed/j-1n3KJR1I8",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Meditation for Beginners - How to Start Your Practice",
                description="This video tutorial will guide you through the basics of starting a meditation practice for mental clarity and peace.",
                content_type="video",
                video_url="https://www.youtube.com/embed/MKEUEWEVTiE",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Relaxation Techniques to Calm Your Nerves",
                description="A short video guide demonstrating effective relaxation techniques, including deep breathing and progressive muscle relaxation.",
                content_type="video",
                video_url="https://www.youtube.com/embed/LiUnFJ8P4gM",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Self-care Tips to De-stress | Mental Wellness Tips",
                description="Watch this informative video to learn simple and effective self-care tips for mental wellness.",
                content_type="video",
                video_url="https://www.youtube.com/embed/AGessEpBxGM",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="The Power of Positive Thinking for Mental Health",
                description="This video explores the importance of maintaining a positive mindset and how it affects mental health.",
                content_type="video",
                video_url="https://www.youtube.com/embed/HwLK9dBQn0g",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Yoga For Beginners: The Ultimate Guide",
                content_type="resource",
                description="A detailed guide for beginners in yoga, covering basic postures, breathing exercises, and tips for starting yoga practice at home.",
                url="https://www.artofliving.org/in-en/yoga",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Yoga for Stress Relief (Full Practice)",
                content_type="video",
                description="A full-length yoga video that guides you through a series of asanas and pranayama to release stress and tension.",
                video_url="https://www.youtube.com/embed/4pKly2JojMw",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Understanding Anxiety and How to Cope",
                description="The ADAA explains the symptoms of anxiety and offers evidence-based coping strategies.",
                url="https://adaa.org/understanding-anxiety",
                content_type="article"
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Practice Gratitude",
                content_type="self_care_tip",
                description="Start each day by writing down 3 things you're grateful for. This small practice can significantly improve your mood and outlook.",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Spend Time Outdoors",
                content_type="self_care_tip",
                description="Nature has healing power. Try to spend at least 30 minutes outdoors each day to improve your mood and reduce stress.",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Set Boundaries",
                content_type="self_care_tip",
                description="Learn to say no when necessary. Setting healthy boundaries can help protect your mental health and increase your emotional resilience.",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Daily Journaling for Mental Clarity",
                content_type="practice",
                description="Write down your thoughts and feelings each day. Journaling can help you process emotions, reduce anxiety, and increase mindfulness.",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Mindfulness Meditation",
                content_type="practice",
                description="Take 5 minutes each day to sit quietly and focus on your breath. Mindfulness meditation can help reduce stress and improve focus.",
            )
            MentalWellbeingContent.objects.get_or_create(
                title="Regular Exercise for Mental Health",
                content_type="practice",
                description="Exercise releases endorphins that boost mood. Aim for 30 minutes of physical activity a day to improve your mental wellbeing.",
            )
        except Exception as e:
            raise CommandError('Setup failed due to an exception "%s"' % e)
        