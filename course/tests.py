from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Course
from curriculum.models import CurriculumMapping
from unittest.mock import patch

class CourseViewTests(TestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.course1 = Course.objects.create(id="CS101", name="Computer Science", year=2025, term=1)
        self.course2 = Course.objects.create(id="MATH101", name="Mathematics", year=2025, term=1)
        self.course3 = Course.objects.create(id="ENG101", name="English Literature", year=2025, term=1)

    def test_course_list(self):
        """Test the CourseList view returns all courses"""
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_course_detail(self):
        """Test retrieving a single course"""
        response = self.client.get(reverse('course-detail', kwargs={'id': self.course1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.course1.id)
        self.assertEqual(response.data['name'], self.course1.name)

    def test_course_not_found(self):
        """Test retrieving a course that does not exist"""
        response = self.client.get(reverse('course-detail', kwargs={'id': 'INVALID_ID'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_search_prefix(self):
        """Test searching for a course by prefix"""
        response = self.client.get(reverse('course-search', kwargs={'search': 'Comp'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.course1.id)

    def test_course_search_keyword(self):
        """Test searching for a course by a keyword appearing anywhere"""
        response = self.client.get(reverse('course-search', kwargs={'search': 'Science'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.course1.id)

    def test_course_search_single_letter(self):
        """Test searching for a course by a single alphabet appearing anywhere"""
        response = self.client.get(reverse('course-search', kwargs={'search': 't'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(course['id'] == 'MATH101' for course in response.data))

    def test_course_search_partial_word(self):
        """Test searching for a course by a partial word match"""
        response = self.client.get(reverse('course-search', kwargs={'search': 'Lit'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.course3.id)

    def test_course_search_no_results(self):
        """Test searching for a course with no match"""
        response = self.client.get(reverse('course-search', kwargs={'search': 'Physics'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch.object(CurriculumMapping, 'get_curriculums_for_course', return_value=[])
    def test_course_curriculums_empty(self, mock_curriculums):
        """Test getting curriculums for a course with no mappings"""
        response = self.client.get(reverse('course-curriculums', kwargs={'course_id': self.course1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"course_id": self.course1.id, "curriculums": []})
