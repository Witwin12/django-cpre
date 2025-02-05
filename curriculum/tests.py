# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Curriculum, CurriculumMapping
from course.models import Course  # Ensure your Course model has fields: id, name, year, term

class CurriculumAPITestCase(APITestCase):
    def setUp(self):
        # Create Course objects
        self.course1 = Course.objects.create(
            id='C001',
            name='Introduction to Programming',
            year=2023,
            term=1  # assuming numeric term, adjust accordingly
        )
        self.course2 = Course.objects.create(
            id='C002',
            name='Data Structures',
            year=2023,
            term=2
        )

        # Create Curriculum objects (note: id is a CharField)
        self.curriculum1 = Curriculum.objects.create(
            id='CURR001',
            name='Computer Science Basics'
        )
        self.curriculum2 = Curriculum.objects.create(
            id='CURR002',
            name='Advanced Computer Science'
        )

        # Create CurriculumMapping objects to associate curriculums with courses
        CurriculumMapping.objects.create(curriculum=self.curriculum1, course=self.course1)
        CurriculumMapping.objects.create(curriculum=self.curriculum1, course=self.course2)
        CurriculumMapping.objects.create(curriculum=self.curriculum2, course=self.course1)

    def test_curriculum_list(self):
        """
        Test that the list view returns all curriculums.
        """
        # Use the correct URL name defined in your urls.py
        url = reverse('curriculumList-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming that the serializer returns at least id and name
        self.assertEqual(len(response.data), 2)
        curriculum_ids = {item['id'] for item in response.data}
        self.assertSetEqual(curriculum_ids, {self.curriculum1.id, self.curriculum2.id})

    def test_curriculum_detail(self):
        """
        Test that the detail view returns the correct curriculum by id.
        """
        url = reverse('curriculum-detail', kwargs={'id': self.curriculum1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.curriculum1.id)
        self.assertEqual(response.data['name'], self.curriculum1.name)

    def test_curriculum_latest_view(self):
        """
        Test that the latest curriculum (by ordering "-id") is returned along with its courses.
        In this test, curriculum2 (CURR002) is assumed to be the latest because its id is higher.
        """
        url = reverse('curriculum-latest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # The latest curriculum should be curriculum2
        self.assertEqual(data['curriculum'], self.curriculum2.name)
        # curriculum2 has one course mapping (course1)
        courses = data.get('courses', [])
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]['id'], self.course1.id)
        self.assertEqual(courses[0]['name'], self.course1.name)

    def test_curriculum_latest_view_no_curriculum(self):
        """
        Test that if no curriculum exists, the latest view returns a 404 with an error message.
        """
        # Delete all curriculums
        Curriculum.objects.all().delete()
        url = reverse('curriculum-latest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "No curriculum found")

    def test_curriculum_courses_view(self):
        """
        Test that the courses view returns the correct courses for a given curriculum.
        """
        url = reverse('curriculum-courses', kwargs={'curriculum_id': self.curriculum1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['curriculum'], self.curriculum1.name)
        courses = data.get('courses', [])
        self.assertEqual(len(courses), 2)
        course_ids = {course['id'] for course in courses}
        self.assertSetEqual(course_ids, {self.course1.id, self.course2.id})

    def test_curriculum_courses_view_not_found(self):
        """
        Test that requesting courses for a non-existent curriculum returns a 404.
        """
        url = reverse('curriculum-courses', kwargs={'curriculum_id': 'NON_EXISTENT'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
