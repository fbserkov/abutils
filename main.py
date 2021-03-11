from evrika.api import load as load_evrika
from jobs.api import check as check_jobs
from journals.api import check as check_journals
from housing.api import sync as sync_housing
from organization.api import sync as sync_organization
from workload.api import plot as plot_workload

from sys import argv
test = len(argv) > 1

plot_workload(run=True, name=None, test=test)
check_jobs(run=True, test=test)
check_journals(run=True, test=test)
load_evrika(run=True, test=test)
sync_housing(run=True, commit=not test, quick=False, test=test)
sync_organization(run=True, commit=not test, test=test)
