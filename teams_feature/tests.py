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
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', last_name='User',
            email='testuser@skyengineering.com'
        )
        self.client.login(username='testuser', password='testpass123')

        self.manager = User.objects.create_user(
            username='dr_sarah', password='testpass123',
            first_name='Sarah', last_name='Chen',
            email='sarah.chen@skyengineering.com'
        )

        self.dept_aerospace = Department.objects.create(
            department_name='Aerospace', description='Aerospace department'
        )
        self.dept_engineering = Department.objects.create(
            department_name='Engineering', description='Engineering department'
        )

        self.team_type = TeamType.objects.create(
            type_name='Engineering', description='Engineering team type'
        )

        self.skill_python = Skill.objects.create(skill_name='Python', category='Programming')
        self.skill_test_automation = Skill.objects.create(skill_name='Test Automation', category='Technical')

        self.propulsion = Team.objects.create(
            team_name='Propulsion Systems', department=self.dept_aerospace,
            manager=self.manager, team_type=self.team_type,
            description='Develops and tests advanced propulsion technologies.',
            purpose='Next generation aircraft propulsion.', is_active=True
        )

        self.propulsion_research = Team.objects.create(
            team_name='Propulsion Research', department=self.dept_aerospace,
            manager=self.manager, description='Research into propulsion systems.', is_active=True
        )

        self.avionics = Team.objects.create(
            team_name='Avionics Integration', department=self.dept_aerospace,
            manager=self.manager, description='Integrates electronic systems.', is_active=True
        )

        self.materials = Team.objects.create(
            team_name='Materials Science', department=self.dept_engineering,
            manager=self.manager, description='Materials research and development.', is_active=True
        )

        self.aircraft = Team.objects.create(
            team_name='Aircraft Integration', department=self.dept_aerospace,
            manager=self.manager, description='Aircraft systems integration.', is_active=True
        )

        self.cloud = Team.objects.create(
            team_name='Cloud Infrastructure', department=self.dept_engineering,
            manager=self.manager, description='Manages cloud architecture and DevOps.', is_active=True
        )

        self.frontend = Team.objects.create(
            team_name='Frontend Testing', department=self.dept_engineering,
            manager=self.manager, description='Frontend testing team.', is_active=True
        )

        self.innovation = Team.objects.create(
            team_name='New Innovation Lab', department=self.dept_engineering,
            manager=self.manager, description='Innovation and research lab.', is_active=True
        )

        for i in range(12):
            TeamMember.objects.create(
                first_name=f'Member{i}', last_name=f'Surname{i}',
                email=f'member{i}@skyengineering.com', role='Engineer', team=self.propulsion
            )

        TeamSkill.objects.create(team=self.propulsion, skill=self.skill_python, proficiency_level='advanced')
        TeamSkill.objects.create(team=self.propulsion, skill=self.skill_test_automation, proficiency_level='intermediate')

        UpstreamDependency.objects.create(
            team=self.propulsion, upstream_team=self.materials,
            description='Relies on materials research for propulsion components.'
        )

        DownstreamDependency.objects.create(
            team=self.propulsion, downstream_team=self.aircraft,
            description='Aircraft integration relies on propulsion systems.'
        )


# ==============================================================================
# TEST PLAN 1: SEARCH FOR TEAMS
# ==============================================================================

class TC1_TeamNameSearch(TeamTestSetup):
    """TC1 — Positive — Search by valid team name returns correct results."""

    # Verifies that searching a real team name returns matching results with 200 status
    def test_search_returns_correct_results(self):
        """Searching 'Propulsion' returns Propulsion Systems and Propulsion Research."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propulsion Systems')
        self.assertContains(response, 'Propulsion Research')

    # Verifies that teams not matching the search term are excluded from results
    def test_search_excludes_non_matching_teams(self):
        """Teams not matching search term are not shown in results."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Propulsion'})
        self.assertNotContains(response, 'Avionics Integration')


class TC2_DepartmentFilter(TeamTestSetup):
    """TC2 — Positive — Department dropdown filters teams correctly."""

    # Verifies that selecting a department shows only teams from that department
    def test_filter_by_aerospace_returns_correct_teams(self):
        """Selecting Aerospace shows only Aerospace teams."""
        response = self.client.get(reverse('teams:team_list'), {'department': 'Aerospace'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propulsion Systems')
        self.assertNotContains(response, 'Cloud Infrastructure')


class TC3_NoResultsEmptyState(TeamTestSetup):
    """TC3 — Negative — Empty state shown when search returns no results."""

    # Verifies that a search with no matches returns an empty queryset
    def test_search_returns_empty_queryset(self):
        """Searching 'Quantum' returns zero teams."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        teams = response.context['teams']
        self.assertEqual(len(teams), 0)

    # Verifies that the empty state message is shown when no results are found
    def test_empty_state_message_displayed(self):
        """'No teams found' message is displayed when search returns nothing."""
        response = self.client.get(reverse('teams:team_list'), {'q': 'Quantum'})
        self.assertContains(response, 'No teams found')


class TC4_SpecialCharactersSearch(TeamTestSetup):
    """TC4 — Negative — Special characters handled safely without errors."""

    # Verifies that special characters in search do not cause a server error
    def test_special_characters_no_error(self):
        """Searching with ('test') does not cause a server error."""
        response = self.client.get(reverse('teams:team_list'), {'q': "('test')"})
        self.assertEqual(response.status_code, 200)

    # Verifies that XSS script tags are not rendered as executable HTML
    def test_xss_script_tag_not_executed(self):
        """XSS script tag in search is not rendered as executable HTML."""
        response = self.client.get(reverse('teams:team_list'), {'q': '<script>alert("xss")</script>'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert("xss")</script>')


class TC5_ViewTeamDetails(TeamTestSetup):
    """TC5 — Positive — Team detail page loads with correct data."""

    # Verifies that the team detail page loads and displays all correct team information
    def test_team_detail_page_loads_with_correct_data(self):
        """Team detail page loads showing name, manager, department and members."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propulsion Systems')
        self.assertContains(response, 'Sarah')
        self.assertContains(response, 'Aerospace')
        self.assertEqual(len(response.context['members']), 12)


class TC6_TeamWithNoDependencies(TeamTestSetup):
    """TC6 — Negative — Team with no dependencies shows empty state messages."""

    # Verifies that both upstream and downstream empty states are shown when no dependencies exist
    def test_no_dependencies_empty_states_shown(self):
        """Both upstream and downstream show empty state messages."""
        response = self.client.get(reverse('teams:team_detail', args=[self.frontend.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no upstream dependencies')
        self.assertContains(response, 'No other teams currently depend')


class TC7_TeamWithNoMembers(TeamTestSetup):
    """TC7 — Negative — Team with no members shows empty state."""

    # Verifies that the empty state message is shown and members queryset is empty
    def test_empty_members_state_shown(self):
        """Empty state message shown and members queryset is empty."""
        response = self.client.get(reverse('teams:team_detail', args=[self.innovation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No members assigned')
        self.assertEqual(len(response.context['members']), 0)


class TC8_UpstreamDependenciesDisplay(TeamTestSetup):
    """TC8 — Positive — Upstream dependencies display correctly with links."""

    # Verifies that the upstream dependency team name and clickable link are present
    def test_upstream_dependency_displayed_with_link(self):
        """Materials Science shown as upstream dependency with clickable link."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Materials Science')
        expected_url = reverse('teams:team_detail', args=[self.materials.id])
        self.assertContains(response, expected_url)


class TC9_DownstreamDependenciesDisplay(TeamTestSetup):
    """TC9 — Positive — Downstream dependencies display correctly with links."""

    # Verifies that the downstream dependency team name and clickable link are present
    def test_downstream_dependency_displayed_with_link(self):
        """Aircraft Integration shown as downstream dependency with clickable link."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Aircraft Integration')
        expected_url = reverse('teams:team_detail', args=[self.aircraft.id])
        self.assertContains(response, expected_url)


class TC10_TeamWithNoBothDependencies(TeamTestSetup):
    """TC10 — Negative — Team with no dependencies on either side displays correctly."""

    # Verifies that both empty states display correctly without any null value errors
    def test_both_dependency_empty_states_display(self):
        """Both upstream and downstream empty states shown without errors."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no upstream dependencies')
        self.assertContains(response, 'No other teams currently depend')
        self.assertNotContains(response, 'None')


class TC11_EmailTeamButton(TeamTestSetup):
    """TC11 — Positive — Email Team button links correctly with team ID."""

    # Verifies that the Email Team button links to the messages compose URL with the correct team ID
    def test_email_team_button_links_correctly(self):
        """Email Team button present and links to messages compose with team ID."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, '/messages/compose/')
        self.assertContains(response, f'to_team={self.propulsion.id}')


class TC12_ScheduleMeetingButton(TeamTestSetup):
    """TC12 — Positive — Schedule Meeting button links correctly with team ID."""

    # Verifies that the Schedule Meeting button links to the schedule create URL with the correct team ID
    def test_schedule_meeting_button_links_correctly(self):
        """Schedule Meeting button present and links to schedule create with team ID."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, '/schedule/create/')
        self.assertContains(response, f'team={self.propulsion.id}')


class TC13_TeamWithMultipleSkills(TeamTestSetup):
    """TC13 — Positive — Team with multiple skills displays all correctly."""

    # Verifies that all skills are displayed with correct proficiency level badges
    def test_skills_displayed_with_proficiency(self):
        """Python and Test Automation skills shown with proficiency badges."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Test Automation')
        self.assertContains(response, 'Advanced')
        self.assertContains(response, 'Intermediate')
        self.assertEqual(len(response.context['skills']), 2)


class TC14_TeamWithNoSkills(TeamTestSetup):
    """TC14 — Negative — Team with no skills shows empty state."""

    # Verifies that the empty state message is shown and skills queryset is empty
    def test_no_skills_empty_state_shown(self):
        """'No skills listed yet' shown and skills queryset is empty."""
        response = self.client.get(reverse('teams:team_detail', args=[self.cloud.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No skills listed yet')
        self.assertEqual(len(response.context['skills']), 0)


# ==============================================================================
# ADDITIONAL NEGATIVE TEST CASES
# ==============================================================================

class TC15_InactiveTeamNotVisible(TeamTestSetup):
    """TC15 — Negative — Inactive teams are hidden from the team list."""

    # Verifies that a team with is_active=False does not appear in the team list
    def test_inactive_team_not_shown(self):
        """Inactive team does not appear in the team list."""
        Team.objects.create(
            team_name='Disbanded Unit', department=self.dept_engineering,
            manager=self.manager, description='Inactive.', is_active=False
        )
        response = self.client.get(reverse('teams:team_list'))
        self.assertNotContains(response, 'Disbanded Unit')


class TC16_AuthenticationProtection(TeamTestSetup):
    """TC16 — Negative — Unauthenticated users are redirected to login."""

    # Verifies that logged out users are redirected to the login page from the team list
    def test_unauthenticated_redirected_from_list(self):
        """Logged out user redirected from team list to login page."""
        self.client.logout()
        response = self.client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    # Verifies that logged out users are redirected to the login page from a team detail page
    def test_unauthenticated_redirected_from_detail(self):
        """Logged out user redirected from team detail to login page."""
        self.client.logout()
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    # Verifies that accessing a non-existent team ID returns a 404 response
    def test_nonexistent_team_returns_404(self):
        """Accessing a team ID that does not exist returns a 404 response."""
        response = self.client.get(reverse('teams:team_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # Verifies that invalid page numbers in pagination are handled safely without crashing
    def test_pagination_invalid_page_does_not_crash(self):
        """Requesting page 999 or non-integer page is handled safely."""
        response = self.client.get(reverse('teams:team_list'), {'page': '999'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('teams:team_list'), {'page': 'abc'})
        self.assertEqual(response.status_code, 200)


class TC17_EmptySearchReturnsAllTeams(TeamTestSetup):
    """TC17 — Negative — Empty search string returns all teams without crashing."""

    # Verifies that an empty search string returns all active teams without crashing
    def test_empty_search_does_not_crash(self):
        """Submitting empty search returns 200 and shows all active teams."""
        response = self.client.get(reverse('teams:team_list'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['teams']), 0)

    # Verifies that searching with only whitespace does not crash the server
    def test_whitespace_only_search_does_not_crash(self):
        """Searching with only spaces does not crash the server."""
        response = self.client.get(reverse('teams:team_list'), {'q': '     '})
        self.assertEqual(response.status_code, 200)

    # Verifies that a SQL injection attempt is safely handled by Django's ORM
    def test_sql_injection_in_search_does_not_crash(self):
        """SQL injection attempt in search is safely handled by Django ORM."""
        response = self.client.get(
            reverse('teams:team_list'),
            {'q': "'; DROP TABLE teams_feature_team; --"}
        )
        self.assertEqual(response.status_code, 200)


class TC18_TeamWithNoManager(TeamTestSetup):
    """TC18 — Negative — Team with no manager shows warning box."""

    # Verifies that the warning box is displayed when a team has no manager assigned
    def test_no_manager_warning_displayed(self):
        """Warning box shown when team has no manager assigned."""
        no_manager_team = Team.objects.create(
            team_name='Unmanaged Team', department=self.dept_engineering,
            manager=None, description='Team with no manager.', is_active=True
        )
        response = self.client.get(reverse('teams:team_detail', args=[no_manager_team.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No manager assigned')

    # Verifies that teams without a manager show Unassigned in the team list
    def test_no_manager_shown_as_unassigned_in_list(self):
        """Team list shows Unassigned when team has no manager."""
        Team.objects.create(
            team_name='Unmanaged Team', department=self.dept_engineering,
            manager=None, description='No manager.', is_active=True
        )
        response = self.client.get(reverse('teams:team_list'))
        self.assertContains(response, 'Unassigned')


class TC19_TeamListPageLoads(TeamTestSetup):
    """TC19 — Positive — Team list page loads correctly with all elements."""

    # Verifies that total_teams and total_members stat counters are passed to the template
    def test_team_list_loads_with_stat_counters(self):
        """Team list page loads with total teams and total members stat counters."""
        response = self.client.get(reverse('teams:team_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_teams', response.context)
        self.assertIn('total_members', response.context)

    # Verifies that the search bar and department dropdown are both present on the page
    def test_search_bar_and_department_filter_present(self):
        """Search bar and department dropdown are both visible on the page."""
        response = self.client.get(reverse('teams:team_list'))
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'name="department"')


class TC20_TeamDetailActionButtons(TeamTestSetup):
    """TC20 — Positive — Both action buttons present on team detail page."""

    # Verifies that both Email Team and Schedule Meeting buttons are visible on the detail page
    def test_email_and_schedule_buttons_both_present(self):
        """Email Team and Schedule Meeting buttons are both visible."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Email Team')
        self.assertContains(response, 'Schedule Meeting')

    # Verifies that breadcrumb navigation showing Teams and the team name is present
    def test_breadcrumb_navigation_present(self):
        """Breadcrumb showing Teams / team name is visible on detail page."""
        response = self.client.get(reverse('teams:team_detail', args=[self.propulsion.id]))
        self.assertContains(response, 'Teams')
        self.assertContains(response, 'Propulsion Systems')