from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, BankAccount
import random


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "phone"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "phone", "is_verified", "created_at"]
        read_only_fields = ["id", "is_verified", "created_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BankAccount
        fields = ["id", "user", "account_number", "account_type", "balance", "status", "created_at"]
        read_only_fields = ["id", "account_number", "balance", "status", "created_at"]

    def create(self, validated_data):
        # Auto generate account number
        account_number = "BANK" + str(random.randint(100000000, 999999999))
        validated_data["account_number"] = account_number
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)