from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils import timezone
from django.core.exceptions import ValidationError

# =========================
# USER MANAGER
# =========================
class CustomUserManager(BaseUserManager):
    """
    Custom manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("approval_level", "DIRECTOR")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

# =========================
# ORGANIZATION MODELS
# =========================
class Department(models.Model):
    """
    Departments within the organization
    One department has exactly one head.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Department Name", help_text="e.g., Information Technology, Human Resources",)
    head = models.OneToOneField("CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="department_headed", verbose_name="Department Head", help_text="The person who leads this department",)
    is_active = models.BooleanField(default=True, verbose_name="Active", help_text="Inactive departments are hidden from selection",)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    Units within a department.
    One unit has exactly one supervisor.
    """
    name = models.CharField(max_length=100, verbose_name="Unit Name", help_text="e.g., Network Team, Backend Development",)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="units", verbose_name="Department",)
    supervisor = models.OneToOneField("CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="unit_supervised", verbose_name="Unit Supervisor", help_text="The person who supervises this unit",)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["department", "name"]
        unique_together = ["department", "name"]
        verbose_name = "Unit"
        verbose_name_plural = "Units"

    def __str__(self):
        return f"{self.department.name} - {self.name}"

class OfficeLocation(models.Model):
    """
    Physical office locations.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Office Location Name", help_text="e.g., Lagos HQ, Abuja Branch",)
    address = models.TextField(verbose_name="Office Address")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Office Location"
        verbose_name_plural = "Office Locations"

    def __str__(self):
        return self.name


# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Monolithic v1 user model.
    Soft delete via is_active.
    """
    # ---------- AUTH ----------
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Used for login - must be unique",
    )

    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    middle_name = models.CharField(max_length=50, blank=True, null=True)

    # ---------- PERSONAL ----------
    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    MARITAL_STATUS_CHOICES = [
        ("SINGLE", "Single"),
        ("MARRIED", "Married"),
        ("DIVORCED", "Divorced"),
        ("WIDOWED", "Widowed"),
    ]
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Nigeria")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees",)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees",)
    office_location = models.ForeignKey(
        OfficeLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
        verbose_name="Reports To",
    )
    EMPLOYEE_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ON_LEAVE", "On Leave"),
        ("SUSPENDED", "Suspended"),
        ("TERMINATED", "Terminated"),
        ("RESIGNED", "Resigned"),
    ]
    employee_status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS_CHOICES,
        default="ACTIVE",
    )
    APPROVAL_LEVEL_CHOICES = [
        ("STAFF", "Staff"),
        ("SUPERVISOR", "Supervisor"),
        ("DEPT_HEAD", "Department Head"),
        ("HR_ADMIN", "HR Admin"),
        ("IT_ADMIN", "IT Admin"),
        ("DEPUTY_DIR", "Deputy Director"),
        ("DIRECTOR", "Director"),
    ]
    approval_level = models.CharField(
        max_length=20,
        choices=APPROVAL_LEVEL_CHOICES,
        default="STAFF",
    )
    date_joined = models.DateField(default=timezone.now)
    is_active = models.BooleanField(
        default=True,
        help_text="Soft delete flag. Deactivated users remain for audit.",
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["department"]),
            models.Index(fields=["approval_level"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    # ---------- VALIDATION ----------
    def clean(self):
        if self.reports_to and self.reports_to == self:
            raise ValidationError("A user cannot report to themselves.")

        if self.unit and self.reports_to:
            if self.unit.department != self.reports_to.department:
                raise ValidationError(
                    "Supervisor must belong to the same department."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ---------- HELPERS ----------
    def can_approve(self):
        return self.approval_level in {
            "SUPERVISOR",
            "DEPT_HEAD",
            "HR_ADMIN",
            "IT_ADMIN",
            "DEPUTY_DIR",
            "DIRECTOR",
        }

    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day)
            < (self.date_of_birth.month, self.date_of_birth.day)
        )