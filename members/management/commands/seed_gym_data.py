"""
seed_gym_data.py — Seeds the IMS database with realistic gym data.

Usage:
    python manage.py seed_gym_data
"""
import random
from datetime import date, timedelta, time
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from members.models import Tag, Member, MembershipPlan, MemberMembership
from services.models import Service, StaffMember, Resource
from bookings.models import Appointment
from billing.models import Payment


MALE_FIRST_NAMES = [
    'Juan', 'Jose', 'Miguel', 'Carlos', 'Antonio', 'Fernando', 'Eduardo',
    'Roberto', 'Angelo', 'Marco', 'Andres', 'Rafael', 'Diego', 'Luis',
    'Ramon', 'Paolo', 'Luca', 'Gabriel', 'Christian', 'Mark', 'John',
    'James', 'Ryan', 'Kevin', 'Michael', 'Daniel', 'Adrian', 'Matthew',
    'Nathan', 'Joshua',
]
FEMALE_FIRST_NAMES = [
    'Maria', 'Ana', 'Rosa', 'Elena', 'Carmen', 'Luisa', 'Isabel',
    'Cristina', 'Luz', 'Patricia', 'Jennifer', 'Michelle', 'Kristine',
    'Maricel', 'Rowena', 'Jasmine', 'Joanna', 'Camille', 'Andrea',
    'Stephanie', 'Nicole', 'Alexandra', 'Katrina', 'Theresa', 'Maribel',
    'Grace', 'Joy', 'Faith', 'Hope', 'Charity',
]
LAST_NAMES = [
    'Santos', 'Reyes', 'Cruz', 'Garcia', 'Torres', 'Flores', 'Mendoza',
    'Rivera', 'Lopez', 'Gonzalez', 'Aquino', 'De Leon', 'Bautista',
    'Ramos', 'Dela Cruz', 'Villanueva', 'Castillo', 'Morales', 'Velasco',
    'Lim', 'Tan', 'Sy', 'Uy', 'Chua', 'Co', 'Ng', 'Yap', 'Lee', 'Chan', 'Wong',
]


def rand_phone():
    return '+639' + ''.join([str(random.randint(0, 9)) for _ in range(9)])


def rand_dob(min_age=18, max_age=55):
    today = date.today()
    days = random.randint(min_age * 365, max_age * 365)
    return today - timedelta(days=days)


def rand_date_past(days=90):
    return date.today() - timedelta(days=random.randint(0, days))


def rand_date_future(days=60):
    return date.today() + timedelta(days=random.randint(1, days))


def rand_time(hour_min=7, hour_max=19):
    hour = random.randint(hour_min, hour_max)
    minute = random.choice([0, 30])
    return time(hour, minute)


class Command(BaseCommand):
    help = 'Seed the database with gym sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding IMS gym data...'))

        # ── Owner ──────────────────────────────────────────────────
        owner, created = User.objects.get_or_create(
            email='owner@fitpeak.com',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'role': 'owner',
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('Admin123!'),
            },
        )
        if created:
            self.stdout.write(f'  Created owner: owner@fitpeak.com / Admin123!')

        # ── Staff ──────────────────────────────────────────────────
        staff_data = [
            ('trainer1@fitpeak.com', 'Marco', 'Reyes', 'Personal Trainer'),
            ('trainer2@fitpeak.com', 'Maria', 'Santos', 'Yoga & Wellness'),
            ('trainer3@fitpeak.com', 'Kevin', 'Lim', 'Boxing & Conditioning'),
        ]
        staff_users = []
        for email, fn, ln, spec in staff_data:
            u, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fn, 'last_name': ln,
                    'role': 'staff', 'is_staff': True,
                    'password': make_password('Staff123!'),
                },
            )
            staff_member, _ = StaffMember.objects.get_or_create(
                user=u,
                defaults={'specialization': spec, 'is_available': True},
            )
            staff_users.append(staff_member)
            if created:
                self.stdout.write(f'  Created staff: {email} / Staff123!')

        # ── Membership Plans ───────────────────────────────────────
        plan_data = [
            ('Day Pass', 1, Decimal('200.00'), 'Single-day access pass'),
            ('Monthly', 30, Decimal('1500.00'), 'Unlimited access for 30 days'),
            ('3-Month', 90, Decimal('4000.00'), '3-month unlimited access — save 11%'),
            ('6-Month', 180, Decimal('7500.00'), '6-month unlimited access — save 17%'),
            ('Annual', 365, Decimal('14000.00'), 'Full year unlimited access — best value'),
        ]
        plans = []
        for name, days, price, desc in plan_data:
            p, _ = MembershipPlan.objects.get_or_create(
                name=name, defaults={'duration_days': days, 'price': price, 'description': desc},
            )
            plans.append(p)
        self.stdout.write(f'  Membership plans: {len(plans)} created/found')

        # ── Services ───────────────────────────────────────────────
        service_data = [
            ('Personal Training', 60, Decimal('800.00'), 'Fitness', '#6366F1'),
            ('Group Fitness Class', 45, Decimal('350.00'), 'Fitness', '#22C55E'),
            ('Yoga', 60, Decimal('400.00'), 'Wellness', '#F59E0B'),
            ('Boxing', 60, Decimal('500.00'), 'Combat Sports', '#EF4444'),
            ('Strength & Conditioning', 75, Decimal('900.00'), 'Fitness', '#3B82F6'),
            ('Nutrition Consultation', 30, Decimal('600.00'), 'Wellness', '#A855F7'),
        ]
        services = []
        for name, dur, price, cat, color in service_data:
            svc, _ = Service.objects.get_or_create(
                name=name,
                defaults={'duration_minutes': dur, 'price': price, 'category': cat, 'color': color},
            )
            services.append(svc)
        self.stdout.write(f'  Services: {len(services)} created/found')

        # Assign services to staff
        for sm in staff_users:
            sm.services.set(random.sample(services, k=random.randint(2, 4)))

        # ── Resources ──────────────────────────────────────────────
        resource_data = [
            ('Boxing Ring', 'Ring', 2),
            ('Yoga Studio', 'Studio', 12),
            ('Weight Room', 'Room', 20),
            ('Group Fitness Room', 'Room', 15),
        ]
        resources = []
        for name, rtype, cap in resource_data:
            r, _ = Resource.objects.get_or_create(
                name=name, defaults={'resource_type': rtype, 'capacity': cap},
            )
            resources.append(r)
        self.stdout.write(f'  Resources: {len(resources)} created/found')

        # ── Tags ───────────────────────────────────────────────────
        tag_data = [
            ('VIP', '#F59E0B'),
            ('Student', '#3B82F6'),
            ('Senior', '#22C55E'),
            ('First-Timer', '#A855F7'),
        ]
        tags = []
        for name, color in tag_data:
            t, _ = Tag.objects.get_or_create(name=name, defaults={'color': color})
            tags.append(t)
        self.stdout.write(f'  Tags: {len(tags)} created/found')

        # ── 100 Members ────────────────────────────────────────────
        members_created = 0
        members = list(Member.objects.all())
        target = 100
        needed = target - len(members)

        for i in range(needed):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(MALE_FIRST_NAMES if gender == 'male' else FEMALE_FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            n = i + 1
            email = f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}{n}@gym.ph"

            if Member.objects.filter(email=email).exists():
                continue

            r = random.random()
            status = 'active' if r < 0.80 else ('inactive' if r < 0.95 else 'archived')

            # Create a User account for this member
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'client',
                    'password': make_password('Member123!'),
                },
            )

            m = Member.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=rand_phone(),
                date_of_birth=rand_dob(),
                status=status,
                notes='',
            )
            # Assign 0–2 random tags
            m.tags.set(random.sample(tags, k=random.randint(0, 2)))
            members.append(m)
            members_created += 1

        # Link User accounts to any existing members that don't have one yet
        for m in Member.objects.filter(user__isnull=True):
            user, _ = User.objects.get_or_create(
                email=m.email,
                defaults={
                    'first_name': m.first_name,
                    'last_name': m.last_name,
                    'role': 'client',
                    'password': make_password('Member123!'),
                },
            )
            m.user = user
            m.save(update_fields=['user'])

        members = list(Member.objects.all())
        self.stdout.write(f'  Members: {members_created} created, {len(members)} total')

        # ── Memberships for active members ─────────────────────────
        active_members = [m for m in members if m.status == 'active']
        memberships_created = 0
        for member in active_members:
            if member.memberships.exists():
                continue
            plan = random.choice(plans)
            start = rand_date_past(180)
            end = start + timedelta(days=plan.duration_days)
            status = 'active' if end >= date.today() else 'expired'
            MemberMembership.objects.create(
                member=member, plan=plan, start_date=start, end_date=end, status=status,
            )
            memberships_created += 1
        self.stdout.write(f'  Memberships: {memberships_created} created')

        # ── ~200 Appointments ──────────────────────────────────────
        appt_created = 0
        statuses_past = ['completed', 'completed', 'completed', 'cancelled', 'no_show']
        statuses_future = ['pending', 'confirmed', 'confirmed']

        for _ in range(200):
            if not members or not services:
                break
            member = random.choice(members)
            service = random.choice(services)
            staff = random.choice(staff_users) if random.random() > 0.2 else None

            is_future = random.random() > 0.6
            appt_date = rand_date_future(60) if is_future else rand_date_past(90)
            start_t = rand_time()
            end_t = time(
                (start_t.hour * 60 + start_t.minute + service.duration_minutes) // 60,
                (start_t.hour * 60 + start_t.minute + service.duration_minutes) % 60,
            )
            if end_t.hour > 20:
                continue

            status = random.choice(statuses_future if is_future else statuses_past)

            try:
                appt = Appointment.objects.create(
                    member=member,
                    service=service,
                    staff=staff,
                    date=appt_date,
                    start_time=start_t,
                    end_time=end_t,
                    status=status,
                    booking_source=random.choice(['staff', 'staff', 'public']),
                    notes='',
                )
                appt_created += 1
            except Exception:
                pass  # Skip conflicts

        self.stdout.write(f'  Appointments: {appt_created} created')

        # ── ~150 Payments ──────────────────────────────────────────
        completed_appts = list(Appointment.objects.filter(status='completed'))
        payment_methods = ['cash', 'gcash', 'maya', 'card', 'bank_transfer']
        payments_created = 0

        for appt in random.sample(completed_appts, k=min(120, len(completed_appts))):
            Payment.objects.create(
                member=appt.member,
                appointment=appt,
                amount=appt.service.price,
                method=random.choice(payment_methods),
                status='paid',
                recorded_by=owner,
                description=f'Payment for {appt.service.name}',
            )
            payments_created += 1

        # Membership payments
        all_memberships = list(MemberMembership.objects.all())
        for mem in random.sample(all_memberships, k=min(30, len(all_memberships))):
            Payment.objects.create(
                member=mem.member,
                membership=mem,
                amount=mem.plan.price,
                method=random.choice(payment_methods),
                status='paid',
                recorded_by=owner,
                description=f'{mem.plan.name} membership payment',
            )
            payments_created += 1

        self.stdout.write(f'  Payments: {payments_created} created')

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
        self.stdout.write('  Owner login: owner@fitpeak.com / Admin123!')
        self.stdout.write('  Staff login: trainer1@fitpeak.com / Staff123!')
        self.stdout.write('  Admin portal: http://localhost:8000/admin-portal/login/')
        self.stdout.write('  Public booking: http://localhost:8000/book/')
