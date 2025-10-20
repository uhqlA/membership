from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from .models import Member
from .serializers import MemberSerializer, MemberCreateSerializer
from .utils import generate_certificate, send_certificate_email
import json


@api_view(['POST'])
def register_member(request):
    try:
        data = request.data

        if 'special_interest' in data:
            if isinstance(data['special_interest'], str):
                try:
                    data['special_interest'] = json.loads(data['special_interest'])
                except:
                    data['special_interest'] = [data['special_interest']]

        serializer = MemberCreateSerializer(data=data)

        if serializer.is_valid():
            member = serializer.save()

            try:
                certificate_path = generate_certificate(member)
                member.certificate_file = certificate_path
                member.certificate_generated = True
                member.save()

                send_certificate_email(member)

            except Exception as e:
                print(f"Error generating certificate: {e}")

            response_data = MemberSerializer(member).data
            return Response({
                'success': True,
                'message': 'Registration successful! Check your email for the certificate.',
                'membership_number': member.membership_number,
                'data': response_data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_availability(request):
    id_passport = request.GET.get('id_passport', None)
    email = request.GET.get('email', None)

    response_data = {}

    if id_passport:
        exists = Member.objects.filter(id_passport=id_passport).exists()
        response_data['id_passport_available'] = not exists
        if exists:
            response_data['message'] = 'This ID/Passport is already registered'

    if email:
        exists = Member.objects.filter(email=email).exists()
        response_data['email_available'] = not exists
        if exists:
            response_data['message'] = 'This email is already registered'

    return Response(response_data)


@api_view(['GET'])
def member_details(request, membership_number):
    try:
        member = Member.objects.get(membership_number=membership_number)
        serializer = MemberSerializer(member)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Member.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Member not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def download_certificate_by_number(request, membership_number):
    try:
        member = Member.objects.get(membership_number=membership_number)

        if not member.certificate_file:
            certificate_path = generate_certificate(member)
            member.certificate_file = certificate_path
            member.certificate_generated = True
            member.save()

        response = FileResponse(
            open(member.certificate_file.path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="NPV_Certificate_{member.membership_number}.pdf"'
        return response

    except Member.DoesNotExist:
        return HttpResponse('Member not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)