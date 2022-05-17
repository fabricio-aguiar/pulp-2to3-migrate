import pytest

from .common_plans import RPM_SIMPLE_PLAN
from .rpm_base import BaseTestRpm
from .util import set_pulp2_snapshot


# @pytest.mark.nightly
@pytest.mark.trylast  # to avoid failures of subsequent tests if the re-installation failed
class TestRemovePlugin(BaseTestRpm):
    """Test the plugin removal functionality."""

    def test_remove_plugin(
        self,
        start_and_check_services,
        stop_and_check_services,
    ):
        """Test that pulp-2to3-migration can be properly removed and installed back."""

        TestRemovePlugin.setUpClass()
        set_pulp2_snapshot(name="rpm_base_4repos")
        self.run_migration(RPM_SIMPLE_PLAN)

        rpm_repo_pre_removal = self.rpm_repo_api.list(name="rpm-with-modules").results[0]
        assert stop_and_check_services() is True

        res = self.smash_cli_client.run(
            ["pulpcore-manager", "remove-plugin", "pulp_2to3_migration"]
        )
        assert "Successfully removed" in res.stdout

        # Some migrations are not reversible and can't be properly unapplied, from that point
        # unapplying of migrations is faked. That problematic migration will be present twice in
        # the output, thus -1.
        num_migrations = res.stdout.count("Unapplying pulp_2to3_migration.") - 1

        # check that after faking migrations and dropping tables explicitly via SQL, pulp starts
        # properly
        assert start_and_check_services() is True

        # Without uninstalling the package just run migrations again to mimic the reinstallation
        # of a plugin at least from pulp's perspective
        assert stop_and_check_services() is True
        res = self.smash_cli_client.run(["pulpcore-manager", "migrate", "pulp_2to3_migration"])
        assert res.stdout.count("Applying pulp_2to3_migration.") == num_migrations

        assert start_and_check_services() is True

        # run migration again and ensure that the same repo is still there, that it was not removed
        # during migration plugin removal.
        self.run_migration(RPM_SIMPLE_PLAN)
        rpm_repo_post_reinstall = self.rpm_repo_api.list(name="rpm-with-modules").results[0]

        assert rpm_repo_pre_removal.pulp_href == rpm_repo_post_reinstall.pulp_href
