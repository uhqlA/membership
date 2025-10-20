from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['membership_number', 'registration_date',
                            'certificate_generated', 'certificate_file',
                            'certificate_sent']

    def get_age(self, obj):
        return obj.get_age()

    def get_full_name(self, obj):
        return obj.get_full_name()

    def validate_id_passport(self, value):
        instance = self.instance
        if instance:
            if Member.objects.exclude(pk=instance.pk).filter(id_passport=value).exists():
                raise serializers.ValidationError(
                    "This ID/Passport number is already registered."
                )
        else:
            if Member.objects.filter(id_passport=value).exists():
                raise serializers.ValidationError(
                    "This ID/Passport number is already registered."
                )
        return value

    def validate_email(self, value):
        instance = self.instance
        if instance:
            if Member.objects.exclude(pk=instance.pk).filter(email=value).exists():
                raise serializers.ValidationError(
                    "This email is already registered."
                )
        else:
            if Member.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "This email is already registered."
                )
        return value

    def validate_phone(self, value):
        import re
        phone_pattern = r'^(\+254|254|07|01)[0-9]{8,9}$'
        if not re.match(phone_pattern, value.replace(' ', '')):
            raise serializers.ValidationError(
                "Please enter a valid Kenyan phone number."
            )
        return value

    def validate_special_interest(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Special interest must be a list."
            )
        return value


class MemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        exclude = ['membership_number', 'registration_date',
                   'certificate_generated', 'certificate_file',
                   'certificate_sent']

    def create(self, validated_data):
        validated_data['phone_verified'] = True
        validated_data['email_verified'] = True
        return super().create(validated_data)
