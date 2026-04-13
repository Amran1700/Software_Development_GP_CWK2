""" Marc Ferandes w2081572 """
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    Team, TeamMember, TeamSkill, Skill, TeamType,
    UpstreamDependency, DownstreamDependency, TeamRepository
)
from organisation_feature.models import Department


class TeamTestSetup(TestCase):
    """
    Base setup class that creates shared test data for all test cases.
    All test classes inherit from this to avoid repeating setup code.
    """

    def setUp(self):
        # Create test user and log in
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            email='testuser@skyengineering.com'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create manager user
        self.manager = User.objects.create_user(
            username='dr_sarah',
            password='testpass123',
            first_name='Sarah',
            last_name='Chen',
            email='sarah.chen@skyengineering.com'
        )

        # Create departments
        self.dept_aerospace = Department.objects.create(
            department_name='Aerospace',
            description='Aerospace department'
        )
        self.dept_operations = Department.objects.create(
            department_name='Operations',
            description='Operations department'
        )
        self.dept_engineering = Department.objects.create(
            department_name='Engineering',
            description='Engineering department'
        )

        # Create team types
        self.team_type = TeamType.objects.create(
            type_name='Engineering',
            description='Engineering team type'
        )

        # Create skills
        self.skill_python = Skill.objects.create(
            skill_name='Python',
            category='Programming'
        )
        self.skill_test_automation = Skill.objects.create(
            skill_name='Test Automation',
            category='Technical'
        )

        # Create main test team — Propulsion Systems (TC1, TC5, TC8, TC9, TC11, TC12, TC13)
        self.propulsion = Team.objects.create(
            team_name='Propulsion Systems',
            department=self.dept_aerospace,
            manager=self.manager,
            team_type=self.team_type,
            description='Develops and tests advanced propulsion technologies.',
            purpose='Next generation aircraft propulsion.',
            is_active=True
        )

        # Create Propulsion Research team (TC1 — second search result)
        self.propulsion_research = Team.objects.create(
            team_name='Propulsion Research',
            department=self.dept_aerospace,
            manager=self.manager,
            description='Research into propulsion systems.',
            is_active=True
        )

        # Create Avionics Integration team (TC2 — Aerospace filter)
        self.avionics = Team.objects.create(
            team_name='Avionics Integration',
            department=self.dept_aerospace,
            manager=self.manager,
            description='Integrates electronic systems.',
            is_active=True
        )

        # Create Materials Science team (TC8 — upstream dependency)
        self.materials = Team.objects.create(
            team_name='Materials Science',
            department=self.dept_engineering,
            manager=self.manager,
            description='Materials research and development.',
            is_active=True
        )

        # Create Aircraft Integration team (TC9 — downstream dependency)
        self.aircraft = Team.objects.create(
            team_name='Aircraft Integration',
            department=self.dept_aerospace,
            manager=self.manager,
            description='Aircraft systems integration.',
            is_active=True
        )

        # Create Cloud Infrastructure team (TC10 — no dependencies)
        self.cloud = Team.objects.create(
            team_name='Cloud Infrastructure',
            department=self.dept_engineering,
            manager=self.manager,
            description='Manages cloud architecture and DevOps.',
            is_active=True
        )

        # Create Frontend Testing team (TC6 — no dependencies)
        self.frontend = Team.objects.create(
            team_name='Frontend Testing',
            department=self.dept_engineering,
            manager=self.manager,
            description='Frontend testing team.',
            is_active=True
        )

        # Create New Innovation Lab team (TC7 — no members)
        self.innovation = Team.objects.create(
            team_name='New Innovation Lab',
            department=self.dept_engineering,
            manager=self.manager,
            description='Innovation and research lab.',
            is_active=True
        )

        # Add 12 members to Propulsion Systems (TC5)
        for i in range(12):
            TeamMember.objects.create(
                first_name=f'Member{i}',
                last_name=f'Surname{i}',
                email=f'member{i}@skyengineering.com',
                role='Engineer',
                team=self.propulsion
            )

        # Add 8 members to Propulsion Research (TC1)
        for i in range(8):
            TeamMember.objects.create(
                first_name=f'Researcher{i}',
                last_name=f'Surname{i}',
                email=f'researcher{i}@skyengineering.com',
                role='Researcher',
                team=self.propulsion_research
            )

        # Add members to Avionics (TC2 — 14 members for stat count)
        for i in range(14):
            TeamMember.objects.create(
                first_name=f'Avionics{i}',
                last_name=f'Engineer{i}',
                email=f'avionics{i}@skyengineering.com',
                role='Engineer',
                team=self.avionics
            )

        # Add skills to Propulsion Systems (TC13)
        TeamSkill.objects.create(
            team=self.propulsion,
            skill=self.skill_python,
            proficiency_level='advanced'
        )
        TeamSkill.objects.create(
            team=self.propulsion,
            skill=self.skill_test_automation,
            proficiency_level='intermediate'
        )

        # Set up upstream dependency: Propulsion depends on Materials Science (TC8)
        UpstreamDependency.objects.create(
            team=self.propulsion,
            upstream_team=self.materials,
            description='Relies on materials research for propulsion components.'
        )

        # Set up downstream dependency: Aircraft Integration depends on Propulsion (TC9)
        DownstreamDependency.objects.create(
            team=self.propulsion,
            downstream_team=self.aircraft,
            description='Aircraft integration relies on propulsion systems.'
        )


# ==============================================================================
# TEST PLAN 1: SEARCH FOR TEAMS
# ==============================================================================

class TC1_TeamNameSearch(TeamTestSetup):
    """
    TC1 — Positive Test
    Verify that users can search for teams by entering a valid team name
    and receive accurate results.
    """

    def test_search_bar_visible_on_teams_page(self):
        """Step 1 — Search bar is visible at the top of the teams page."""
        response = self.client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="q"')

    def test_search_field_accepts_input(self):
        """Step 2 & 3 — Search field accepts text input and submits via GET param."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertEqual(response.status_code, 200)

    def test_search_returns_correct_results(self):
        """Step 4 & 5 — Searching 'Propulsion' returns Propulsion Systems and Propulsion Research."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propulsion Systems')
        self.assertContains(response, 'Propulsion Research')

    def test_search_returns_correct_number_of_results(self):
        """Step 5 — Search for 'Propulsion' returns exactly 2 teams."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        teams = response.context['teams']
        self.assertEqual(teams.count(), 2)

    def test_search_excludes_non_matching_teams(self):
        """Step 5 — Teams not matching 'Propulsion' are not shown in results."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertNotContains(response, 'Avionics Integration')
        self.assertNotContains(response, 'Cloud Infrastructure')


class TC2_DepartmentFilter(TeamTestSetup):
    """
    TC2 — Positive Test
    Verify that users can filter teams by selecting a specific department
    from the dropdown.
    """

    def test_department_dropdown_visible(self):
        """Step 1 — Department dropdown filter is visible on the teams list page."""
        response = self.client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="department"')
        self.assertContains(response, 'All Departments')

    def test_dropdown_contains_department_options(self):
        """Step 2 — Dropdown contains department options from the database."""
        response = self.client.get(reverse('teams:team_list'))
        self.assertContains(response, 'Aerospace')

    def test_filter_by_aerospace_returns_correct_teams(self):
        """Step 3 & 4 — Selecting Aerospace shows only Aerospace teams."""
        response = self.client.get(reverse('teams:team_list'), {'department': 'Aerospace'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propulsion Systems')
        self.assertContains(response, 'Avionics Integration')

    def test_filter_excludes_non_aerospace_teams(self):
        """Step 4 — Non-Aerospace teams are not shown when Aerospace filter is active."""
        response = self.client.get(reverse('teams:team_list'), {'department': 'Aerospace'})
        self.assertNotContains(response, 'Cloud Infrastructure')

    def test_filter_updates_url_with_department_param(self):
        """Step 5 — URL updates to include department GET parameter."""
        response = self.client.get(reverse('teams:team_list'), {'department': 'Aerospace'})
        self.assertIn('department=Aerospace', response.wsgi_request.get_full_path())

    def test_department_context_passed_to_template(self):
        """Step 5 — Department filter value is passed back to template context."""
        response = self.client.get(reverse('teams:team_list'), {'department': 'Aerospace'})
        self.assertEqual(response.context['department'], 'Aerospace')


class TC3_NoResultsEmptyState(TeamTestSetup):
    """
    TC3 — Negative Test
    Verify that the system displays an appropriate message when a search
    query returns no matching teams.
    """

    def test_search_with_no_results_returns_200(self):
        """Step 1-3 — Searching for non-existent team returns 200 without crashing."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        self.assertEqual(response.status_code, 200)

    def test_search_returns_empty_queryset(self):
        """Step 4 — Searching 'Quantum' returns zero teams."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        teams = response.context['teams']
        self.assertEqual(teams.count(), 0)

    def test_empty_state_message_displayed(self):
        """Step 4 & 5 — 'No teams found' message is displayed when search returns nothing."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        self.assertContains(response, 'No teams found')

    def test_clear_filters_button_shown(self):
        """Step 5 — Clear filters button is displayed when no results found."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        self.assertContains(response, 'Clear filters')


class TC4_SpecialCharactersSearch(TeamTestSetup):
    """
    TC4 — Negative Test
    Verify that the system handles special characters in search queries
    without errors or security vulnerabilities.
    """

    def test_special_characters_single_quotes_no_error(self):
        """Step 1-4 — Searching with ('test') does not cause a server error."""
        response = self.client.get(reverse('teams:team_list'), {'q': "('test')"})
        self.assertEqual(response.status_code, 200)

    def test_special_characters_treated_as_plain_text(self):
        """Step 4 & 5 — Special characters are treated as plain text, no JS execution."""
        response = self.client.get(reverse('teams:team_list'), {'q': "('test')"})
        self.assertNotContains(response, '<script>')
        self.assertNotContains(response, 'alert(')

    def test_special_characters_returns_empty_results(self):
        """Step 7 — Searching ('test') returns zero results as no team has that name."""
        response = self.client.get(reverse('teams:team_list'), {'q': "('test')"})
        teams = response.context['teams']
        self.assertEqual(teams.count(), 0)

    def test_hash_dollar_percent_no_error(self):
        """Step 7 — Searching @#$% does not cause a server error."""
        response = self.client.get(reverse('teams:team_list'), {'q': '@#$%'})
        self.assertEqual(response.status_code, 200)

    def test_xss_script_tag_not_executed(self):
        """Security — XSS script tag in search is not rendered as executable HTML."""
        response = self.client.get(reverse('teams:team_list'), {'q': '<script>alert("xss")</script>'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert("xss")</script>')


# ==============================================================================
# TEST PLAN 2: VIEW TEAM DETAILS
# ==============================================================================

class TC5_ViewTeamDetails(TeamTestSetup):
    """
    TC5 — Positive Test
    Verify that clicking on a team from the list displays team details.
    """

    def test_team_detail_page_loads(self):
        """Step 1-3 — Clicking Propulsion Systems row loads the team detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertEqual(response.status_code, 200)

    def test_team_name_displayed(self):
        """Step 4 — Team name is displayed on the detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Propulsion Systems')

    def test_manager_section_displayed(self):
        """Step 4 — Manager section is visible with correct manager name."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Sarah')
        self.assertContains(response, 'Chen')

    def test_department_displayed(self):
        """Step 5 — Department shown as Aerospace."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Aerospace')

    def test_member_count_correct(self):
        """Step 5 — 12 members are shown for Propulsion Systems."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        members = response.context['members']
        self.assertEqual(len(members), 12)

    def test_email_team_button_present(self):
        """Step 6 — Email Team button is present on the detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Email Team')

    def test_schedule_meeting_button_present(self):
        """Step 6 — Schedule Meeting button is present on the detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Schedule Meeting')


class TC6_TeamWithNoDependencies(TeamTestSetup):
    """
    TC6 — Negative Test
    Verify that the system correctly displays a team that has no upstream
    or downstream dependencies.
    """

    def test_team_with_no_dependencies_loads(self):
        """Step 1-3 — Frontend Testing team detail page loads without errors."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertEqual(response.status_code, 200)

    def test_upstream_empty_state_shown(self):
        """Step 4 & 5 — Upstream dependencies section shows empty state message."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertContains(response, 'no upstream dependencies')

    def test_downstream_empty_state_shown(self):
        """Step 5 — Downstream dependencies section shows empty state message."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertContains(response, 'No other teams currently depend')

    def test_upstream_queryset_is_empty(self):
        """Step 5 — Upstream dependencies queryset returns zero items."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertEqual(len(response.context['upstream']), 0)

    def test_downstream_queryset_is_empty(self):
        """Step 5 — Downstream dependencies queryset returns zero items."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertEqual(len(response.context['downstream']), 0)


# ==============================================================================
# TEST PLAN 3: DISPLAY TEAM DEPENDENCIES
# ==============================================================================

class TC7_TeamWithNoMembers(TeamTestSetup):
    """
    TC7 — Negative Test
    Verify system behavior when displaying a team that has no members assigned.
    """

    def test_team_with_no_members_page_loads(self):
        """Step 1-3 — New Innovation Lab detail page loads without errors."""
        response = self.client.get(reverse('teams:team_detail', args=[self.innovation.id]))
        self.assertEqual(response.status_code, 200)

    def test_members_section_visible(self):
        """Step 4 — Team Members section is visible on the page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.innovation.id]))
        self.assertContains(response, 'Team Members')

    def test_empty_members_state_shown(self):
        """Step 5 — Empty state message shown when team has no members."""
        response = self.client.get(reverse('teams:team_detail', args=[self.innovation.id]))
        self.assertContains(response, 'No members assigned')

    def test_members_queryset_is_empty(self):
        """Step 5 — Members queryset returns zero items for Innovation Lab."""
        response = self.client.get(reverse('teams:team_detail', args=[self.innovation.id]))
        members = response.context['members']
        self.assertEqual(len(members), 0)


class TC8_UpstreamDependenciesDisplay(TeamTestSetup):
    """
    TC8 — Positive Test
    Verify that upstream dependencies are correctly displayed with
    accurate team information and clickable navigation links.
    """

    def test_upstream_dependencies_section_visible(self):
        """Step 1 — TEAM DEPENDENCIES section is clearly visible."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upstream Dependencies')

    def test_upstream_team_name_displayed(self):
        """Step 4 — Materials Science is displayed as upstream dependency."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Materials Science')

    def test_upstream_link_navigates_to_correct_team(self):
        """Step 5 & 6 — Upstream team link navigates to Materials Science detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.materials.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Materials Science')

    def test_upstream_queryset_has_correct_count(self):
        """Step 4 — Propulsion Systems has exactly 1 upstream dependency."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        upstream = response.context['upstream']
        self.assertEqual(len(upstream), 1)

    def test_upstream_dependency_link_in_template(self):
        """Step 5 — Upstream team link is present in the rendered HTML."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        expected_url = reverse('teams:team_detail', args=[self.materials.id])
        self.assertContains(response, expected_url)


class TC9_DownstreamDependenciesDisplay(TeamTestSetup):
    """
    TC9 — Positive Test
    Verify that downstream dependencies are correctly displayed with
    accurate team information and bidirectional navigation confirmed.
    """

    def test_downstream_dependencies_section_visible(self):
        """Step 1 & 2 — Downstream Teams subsection is visible."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Downstream')

    def test_downstream_team_name_displayed(self):
        """Step 4 — Aircraft Integration is shown as downstream dependency."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Aircraft Integration')

    def test_downstream_queryset_has_correct_count(self):
        """Step 4 — Propulsion Systems has exactly 1 downstream dependency."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        downstream = response.context['downstream']
        self.assertEqual(len(downstream), 1)

    def test_downstream_link_navigates_correctly(self):
        """Step 6 & 7 — Clicking Aircraft Integration navigates to its detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.aircraft.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aircraft Integration')

    def test_downstream_dependency_link_in_template(self):
        """Step 6 — Downstream team link is present in the rendered HTML."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        expected_url = reverse('teams:team_detail', args=[self.aircraft.id])
        self.assertContains(response, expected_url)


class TC10_TeamWithNoDependencies(TeamTestSetup):
    """
    TC10 — Negative Test
    Verify that a team with neither upstream nor downstream dependencies
    displays correctly without broken UI elements.
    """

    def test_cloud_team_detail_loads(self):
        """Step 1-3 — Cloud Infrastructure team detail page loads successfully."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertEqual(response.status_code, 200)

    def test_dependencies_section_visible(self):
        """Step 4 — TEAM DEPENDENCIES section header is visible."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertContains(response, 'Upstream Dependencies')

    def test_upstream_empty_state(self):
        """Step 5 — Upstream shows 'no upstream dependencies' message."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertContains(response, 'no upstream dependencies')

    def test_downstream_empty_state(self):
        """Step 6 — Downstream shows 'no downstream dependencies' message."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertContains(response, 'No other teams currently depend')

    def test_no_broken_links_or_null_values(self):
        """Step 6 — Page renders without template errors or null value crashes."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'None')


# ==============================================================================
# TEST PLAN 4: EMAIL TEAM BUTTON
# ==============================================================================

class TC11_EmailTeamButtonNavigation(TeamTestSetup):
    """
    TC11 — Positive Test
    Verify that clicking the Email Team button correctly redirects
    to the Messages module.
    """

    def test_email_team_button_visible(self):
        """Step 1 — Email Team button is visible on the team detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Email Team')

    def test_email_team_button_has_correct_link(self):
        """Step 2 — Email Team button links to the messages compose URL."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, '/messages/compose/')

    def test_email_team_button_passes_team_id(self):
        """Step 2 — Email Team button URL includes the team ID as a query param."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        expected = f'to_team={self.propulsion.id}'
        self.assertContains(response, expected)


class TC12_EmailTeamPreFillsRecipient(TeamTestSetup):
    """
    TC12 — Positive Test
    Verify that when redirected to Messages module, the recipient field
    is automatically pre-filled with the team's information.
    """

    def test_email_button_url_contains_team_id(self):
        """Step 1 & 2 — Email Team button URL passes team ID for pre-filling recipient."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, f'to_team={self.propulsion.id}')

    def test_email_button_present_in_header_and_sidebar(self):
        """Step 1 — Email Team button appears in both header and Quick Actions sidebar."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        content = response.content.decode()
        count = content.count('Email Team')
        self.assertGreaterEqual(count, 2)


# ==============================================================================
# TEST PLAN 5: DISPLAY TEAM SKILLS
# ==============================================================================

class TC13_TeamWithMultipleSkills(TeamTestSetup):
    """
    TC13 — Positive Test
    Verify that a team with multiple skills displays all skills correctly.
    """

    def test_skills_section_visible(self):
        """Step 2 — Skills & Expertise section is visible in the right column."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Skills')

    def test_python_skill_displayed(self):
        """Step 3 — Python skill is displayed as a badge."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Python')

    def test_test_automation_skill_displayed(self):
        """Step 3 — Test Automation skill is displayed as a badge."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Test Automation')

    def test_correct_number_of_skills(self):
        """Step 3 — Exactly 2 skills are in the skills queryset."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        skills = response.context['skills']
        self.assertEqual(len(skills), 2)

    def test_proficiency_level_displayed(self):
        """Step 4 — Proficiency level badge is shown for each skill."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Advanced')
        self.assertContains(response, 'Intermediate')


class TC14_TeamWithNoSkills(TeamTestSetup):
    """
    TC14 — Negative Test
    Verify that a team with no skills assigned displays an appropriate empty state.
    """

    def test_team_with_no_skills_page_loads(self):
        """Step 1-3 — Team with no skills detail page loads without errors."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertEqual(response.status_code, 200)

    def test_skills_section_still_visible(self):
        """Step 4 — Skills section is still visible even when empty."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertContains(response, 'Skills')

    def test_no_skills_empty_state_message(self):
        """Step 5 — 'No skills listed yet' empty state message is displayed."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertContains(response, 'No skills listed yet')

    def test_skills_queryset_is_empty(self):
        """Step 5 — Skills queryset returns zero items for a team with no skills."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        skills = response.context['skills']
        self.assertEqual(len(skills), 0)


# ==============================================================================
# AUTHENTICATION TESTS
# ==============================================================================

class AuthenticationTests(TestCase):
    """
    Additional tests to verify @login_required protection on all views.
    """

    def test_team_list_redirects_unauthenticated_user(self):
        """Unauthenticated users are redirected to login when accessing /teams/."""
        client = Client()
        response = client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_team_detail_redirects_unauthenticated_user(self):
        """Unauthenticated users are redirected to login when accessing a team detail page."""
        client = Client()
        response = client.get(reverse('teams:team_detail', args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_nonexistent_team_returns_404(self):
        """Accessing a team ID that does not exist returns a 404 response."""
        user = User.objects.create_user(username='tester', password='pass123')
        client = Client()
        client.login(username='tester', password='pass123')
        response = client.get(reverse('teams:team_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

class TC22_TeamDetailWithInvalidId(TeamTestSetup):
    """
    TC22 — Negative Test
    Verify that accessing a team detail page with a string instead of
    an integer ID returns a 404 and does not crash the server.
    """

    def test_string_id_in_url_returns_404(self):
        """Accessing /teams/abc/ with a non-integer ID returns 404."""
        response = self.client.get('/teams/abc/')
        self.assertEqual(response.status_code, 404)

    def test_zero_id_returns_404(self):
        """Accessing /teams/0/ returns 404 as no team has ID of zero."""
        response = self.client.get('/teams/0/')
        self.assertEqual(response.status_code, 404)

    def test_very_large_id_returns_404(self):
        """Accessing /teams/999999/ returns 404 as that team does not exist."""
        response = self.client.get(reverse('teams:team_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)


class TC23_SearchWithOnlySpaces(TeamTestSetup):
    """
    TC23 — Negative Test
    Verify that searching with only whitespace or blank input
    does not crash the server and returns all teams.
    """

    def test_whitespace_search_returns_all_teams(self):
        """Searching with only spaces returns all active teams."""
        response = self.client.get(reverse('teams:team_list'), {'q': '     '})
        self.assertEqual(response.status_code, 200)

    def test_tab_character_search_does_not_crash(self):
        """Searching with a tab character does not crash the server."""
        response = self.client.get(reverse('teams:team_list'), {'q': '\t'})
        self.assertEqual(response.status_code, 200)

    def test_newline_character_search_does_not_crash(self):
        """Searching with a newline character does not crash the server."""
        response = self.client.get(reverse('teams:team_list'), {'q': '\n'})
        self.assertEqual(response.status_code, 200)


class TC24_UnauthenticatedAccessAttempts(TeamTestSetup):
    """
    TC24 — Negative Test
    Verify that unauthenticated users cannot access any team pages
    and are redirected to the login page in all cases.
    """

    def test_unauthenticated_cannot_access_team_list(self):
        """Logged out user is redirected away from /teams/."""
        self.client.logout()
        response = self.client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_unauthenticated_cannot_access_team_detail(self):
        """Logged out user is redirected away from team detail page."""
        self.client.logout()
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_unauthenticated_cannot_access_team_with_search(self):
        """Logged out user is redirected even when using search params."""
        self.client.logout()
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])
        



# Create your tests here.
