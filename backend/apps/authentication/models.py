"""
TreasuryMind AI - Authentication Models
Custom user model with role-based access control
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    TREASURY_MANAGER = 'treasury_manager', 'Treasury Manager'
    FINANCE_ANALYST = 'finance_analyst', 'Finance Analyst'
    APPROVER = 'approver', 'Approver'


class UserManager(BaseUserManager):
    """Custom manager for User model with email as unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for TreasuryMind AI.
    Uses email as the primary identifier with role-based permissions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=30, choices=UserRole.choices, default=UserRole.FINANCE_ANALYST)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    avatar_url = models.URLField(blank=True)
    notification_preferences = models.JSONField(default=dict)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_approver(self):
        return self.role in [UserRole.ADMIN, UserRole.APPROVER]

    @property
    def can_manage_transactions(self):
        return self.role in [UserRole.ADMIN, UserRole.TREASURY_MANAGER, UserRole.FINANCE_ANALYST]
