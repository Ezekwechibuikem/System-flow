from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    """
    Custom manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with email and password
        """
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with admin privileges
        Superusers can access Django admin and have all permissions
        """
        # Set required flags for superuser
        extra_fields.setdefault('is_staff', True)       
        extra_fields.setdefault('is_superuser', True)   
        extra_fields.setdefault('is_active', True)      
        extra_fields.setdefault('approval_level', 'DIRECTOR')  
        
        # Validate flags
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    # ========== AUTHENTICATION ==========
    email = models.EmailField(unique=True, verbose_name='Email Address', help_text='Used for login - must be unique')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Middle Name')
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Gender')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of Birth')
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True, verbose_name='Marital Status')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Phone Number')
    alternate_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Alternate Phone')
    address = models.TextField(blank=True, null=True, verbose_name='Residential Address')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name='State')
    country = models.CharField(max_length=100, default='Nigeria', verbose_name='Country')
    nationality = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nationality')
    state_of_origin = models.CharField(max_length=100, blank=True, null=True, verbose_name='State of Origin')
    religion = models.CharField(max_length=50, blank=True, null=True, verbose_name='Religion')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,blank=True, related_name='employees',  verbose_name='Department')  
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name='Unit/Team')
    date_joined = models.DateField(default=timezone.now, verbose_name='Date Joined Company', help_text='Employee account creation date')
    
    EMPLOYEE_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('SUSPENDED', 'Suspended'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
    ]
    employee_status = models.CharField(max_length=20, choices=EMPLOYEE_STATUS_CHOICES, default='ACTIVE', verbose_name='Employee Status', help_text='Current employment status - affects attendance')
    #office_location = models.CharField(max_length=200, blank=True, null=True, verbose_name='Office Location',help_text='Physical office location if applicable')
    
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name='Reports To (Manager/Supervisor)', help_text='Direct manager/supervisor')
    
    APPROVAL_LEVEL_CHOICES = [
        ('STAFF', 'Staff (No Approval Power)'),
        ('SUPERVISOR', 'Supervisor'),
        ('DEPT_HEAD', 'Department Head'),
        ('HR_ADMIN', 'HR Admin'),
        ('IT_ADMIN', 'IT Admin'),
        ('DEPUTY_DIR', 'Deputy Director'),
        ('DIRECTOR', 'Director'),
    ]
    approval_level = models.CharField(max_length=20, choices=APPROVAL_LEVEL_CHOICES, default='STAFF', verbose_name='Approval Level', help_text='Determines what the user can approve')
    
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bank Name')
    account_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Account Number')
    account_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Account Name')
    tax_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tax ID / NIN', help_text='National Identification Number or Tax ID')
    
    # ========== EMERGENCY CONTACT ==========
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Emergency Contact Name')
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True, verbose_name='Relationship', help_text='e.g., Spouse, Parent, Sibling')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Emergency Contact Phone')            
    emergency_contact_address = models.TextField(blank=True, null=True, verbose_name='Emergency Contact Address')
    
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name='Profile Picture')
    
    # ========== SYSTEM PERMISSIONS ==========
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Active',
        help_text='Can this user log in?'
    )
    
    is_staff = models.BooleanField(
        default=False, 
        verbose_name='Staff Status (Can access admin)',
        help_text='Allow access to Django admin panel'
    )
    
    is_superuser = models.BooleanField(
        default=False, 
        verbose_name='Superuser Status',
        help_text='Has all permissions without explicitly assigning them'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Last Login')
    
    # ========== MANAGER & AUTHENTICATION CONFIG ==========
    objects = CustomUserManager()  
    
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['first_name', 'last_name']  
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']  
        indexes = [
            # Database indexes for faster queries
            models.Index(fields=['email']),
            models.Index(fields=['department']),
            models.Index(fields=['approval_level']),
        ]
    
    def __str__(self):
        """String representation: John Doe (john@example.com)"""
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """
        Returns full name with middle name if available
        Example: John Michael Doe or John Doe
        """
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        """Returns first name only"""
        return self.first_name
    
    def can_approve(self):
        """
        Check if user has approval authority
        Returns True if user is Supervisor, Dept Head, Director,IT lead, Deputy Director or HR Admin
        Used in attendance approval workflow
        """
        return self.approval_level in [
            'SUPERVISOR', 
            'DEPT_HEAD',
            'HR_ADMIN',
            'IT_ADMIN', 
            'DEPUTY_DIR', 
            'DIRECTOR', 
        ]
    
    def get_subordinates(self):
        """
        Get all employees reporting to this user
        Returns QuerySet of CustomUser objects
        """
        return CustomUser.objects.filter(reports_to=self)
    
    def age(self):
        """
        Calculate age from date of birth
        Returns integer or None if DOB not set
        """
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    # ========== HELPER METHODS FOR ORGANIZATIONAL STRUCTURE ==========
    def get_supervisor(self):
        """
        Get this employee's direct supervisor from their unit
        Returns CustomUser object or None
        
        CRITICAL FOR ATTENDANCE APPROVAL:
        This is used to determine who reviews attendance approval requests
        """
        if self.unit and self.unit.supervisor:
            return self.unit.supervisor
        return None
    
    def get_department_head(self):
        """
        Get this employee's department head
        Returns CustomUser object or None
        """
        if self.department and self.department.head:
            return self.department.head
        return None
    
    def is_department_head(self):
        """
        Check if this user is a department head
        Returns True if user.department_headed exists
        """
        return hasattr(self, 'department_headed')
    
    def is_unit_supervisor(self):
        """
        Check if this user is a unit supervisor
        Returns True if user.unit_supervised exists
        """
        return hasattr(self, 'unit_supervised')
    
    def is_currently_suspended(self):
        """
        Check if employee is currently suspended
        Simply checks employee_status field
        Returns True/False
        
        CRITICAL FOR ATTENDANCE:
        Suspended employees cannot clock in/out
        """
        return self.employee_status == 'SUSPENDED'
    
    
    def clean(self):
        """
        Custom validation logic
        Ensures that a user cannot be their own supervisor
        """
        if self.reports_to and self.reports_to == self:
            raise ValidationError("A user cannot report to themselves.")