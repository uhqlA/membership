from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'membership_number', 'surname', 'other_names',
        'email', 'phone', 'county', 'constituency',
        'membership_category', 'registration_date',
        'certificate_generated', 'certificate_sent'
    ]
    list_filter = [
        'membership_category', 'gender', 'county',
        'registration_date', 'certificate_generated',
        'certificate_sent', 'is_active'
    ]
    search_fields = [
        'surname', 'other_names', 'email', 'phone',
        'membership_number', 'id_passport'
    ]
    readonly_fields = [
        'membership_number', 'registration_date',
        'certificate_file'
    ]

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'surname', 'other_names', 'id_passport',
                'phone', 'email', 'gender', 'ethnicity',
                'religion', 'dob'
            )
        }),
        ('Special Interests', {
            'fields': ('special_interest', 'pwd_number')
        }),
        ('Location', {
            'fields': (
                'county', 'constituency', 'ward', 'polling_station'
            )
        }),
        ('Membership', {
            'fields': (
                'membership_category', 'membership_number',
                'registration_date', 'is_active'
            )
        }),
        ('Verification', {
            'fields': ('phone_verified', 'email_verified')
        }),
        ('Certificate', {
            'fields': (
                'certificate_generated', 'certificate_file',
                'certificate_sent'
            )
        }),
    )

    actions = ['generate_certificates', 'send_certificates']

    def generate_certificates(self, request, queryset):
        from .utils import generate_certificate
        count = 0
        for member in queryset:
            try:
                certificate_path = generate_certificate(member)
                member.certificate_file = certificate_path
                member.certificate_generated = True
                member.save()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error for {member}: {e}', level='ERROR')

        self.message_user(request, f'Successfully generated {count} certificates')

    generate_certificates.short_description = 'Generate certificates for selected members'

    def send_certificates(self, request, queryset):
        from .utils import send_certificate_email
        count = 0
        for member in queryset:
            if member.certificate_file:
                try:
                    if send_certificate_email(member):
                        count += 1
                except Exception as e:
                    self.message_user(request, f'Error for {member}: {e}', level='ERROR')

        self.message_user(request, f'Successfully sent {count} certificates')

    send_certificates.short_description = 'Send certificates to selected members'
