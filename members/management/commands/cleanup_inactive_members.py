"""
cleanup_inactive_members.py

- Members with no appointments in 3+ months → set status to 'inactive'
- Members already inactive with no appointments in 6+ months → delete from DB

Run manually:
    python manage.py cleanup_inactive_members

Or schedule via cron (e.g. daily at midnight):
    0 0 * * * cd /path/to/ims && python manage.py cleanup_inactive_members
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models import Member
from bookings.models import Appointment


class Command(BaseCommand):
    help = 'Mark inactive members and delete long-inactive members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would happen without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now().date()
        three_months_ago = now - timedelta(days=90)
        six_months_ago = now - timedelta(days=180)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made\n'))

        # Members with a recent appointment (within 3 months)
        active_member_ids = set(
            Appointment.objects.filter(date__gte=three_months_ago)
            .values_list('member_id', flat=True)
        )

        # ── Step 1: Active → Inactive (no appointment in 3+ months) ──
        to_inactivate = Member.objects.filter(
            status='active'
        ).exclude(id__in=active_member_ids)

        inactivated = 0
        for member in to_inactivate:
            if dry_run:
                self.stdout.write(f'  [would inactivate] {member.get_full_name()} <{member.email}>')
            else:
                member.status = 'inactive'
                member.save(update_fields=['status'])
            inactivated += 1

        label = 'Would inactivate' if dry_run else 'Inactivated'
        self.stdout.write(f'{label}: {inactivated} member(s) (no activity in 3+ months)')

        # ── Step 2: Inactive → Delete (no appointment in 6+ months) ──
        active_member_ids_6m = set(
            Appointment.objects.filter(date__gte=six_months_ago)
            .values_list('member_id', flat=True)
        )

        to_delete = Member.objects.filter(
            status='inactive'
        ).exclude(id__in=active_member_ids_6m)

        deleted = 0
        for member in to_delete:
            if dry_run:
                self.stdout.write(f'  [would delete] {member.get_full_name()} <{member.email}>')
            else:
                # Also delete the linked User account
                if member.user:
                    member.user.delete()  # cascades to member
                else:
                    member.delete()
            deleted += 1

        label = 'Would delete' if dry_run else 'Deleted'
        self.stdout.write(f'{label}: {deleted} member(s) (inactive for 6+ months)')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS('\nCleanup complete.'))
