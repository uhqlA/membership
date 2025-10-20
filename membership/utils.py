import os
from django.conf import settings
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black
from datetime import datetime


def generate_certificate(member):
    cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)

    filename = f'NPV_Certificate_{member.membership_number}.pdf'
    filepath = os.path.join(cert_dir, filename)

    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)

    npv_green = HexColor('#28a745')
    npv_gold = HexColor('#FFD700')
    dark_gray = HexColor('#333333')

    c.setStrokeColor(npv_green)
    c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, width - inch, height - inch)

    c.setStrokeColor(npv_gold)
    c.setLineWidth(1)
    c.rect(0.6 * inch, 0.6 * inch, width - 1.2 * inch, height - 1.2 * inch)

    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(npv_green)
    c.drawCentredString(width / 2, height - 1.5 * inch, "NATIONAL PEOPLE'S VOICE")

    c.setFont("Helvetica-Oblique", 14)
    c.setFillColor(dark_gray)
    c.drawCentredString(width / 2, height - 1.9 * inch, '"Our Voice, Our Strength"')

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(npv_gold)
    c.drawCentredString(width / 2, height - 2.7 * inch, "CERTIFICATE OF MEMBERSHIP")

    c.setStrokeColor(npv_green)
    c.setLineWidth(2)
    c.line(width / 2 - 3 * inch, height - 2.9 * inch, width / 2 + 3 * inch, height - 2.9 * inch)

    c.setFont("Helvetica", 14)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 3.5 * inch, "This is to certify that")

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(npv_green)
    member_name = member.get_full_name().upper()
    c.drawCentredString(width / 2, height - 4.1 * inch, member_name)

    name_width = c.stringWidth(member_name, "Helvetica-Bold", 24)
    c.setStrokeColor(npv_gold)
    c.setLineWidth(1)
    c.line(width / 2 - name_width / 2, height - 4.2 * inch, width / 2 + name_width / 2, height - 4.2 * inch)

    c.setFont("Helvetica", 14)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 4.7 * inch, "is a registered member of the National People's Voice Party")
    c.drawCentredString(width / 2, height - 5.1 * inch, "and has been granted full membership rights and privileges")

    details_y = height - 6.2 * inch
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(dark_gray)

    c.drawString(2 * inch, details_y, "Membership Number:")
    c.drawString(2 * inch, details_y - 0.3 * inch, "Category:")
    c.drawString(2 * inch, details_y - 0.6 * inch, "ID/Passport:")

    c.setFont("Helvetica", 12)
    c.setFillColor(npv_green)
    c.drawString(4 * inch, details_y, member.membership_number)
    c.drawString(4 * inch, details_y - 0.3 * inch, member.membership_category)
    c.drawString(4 * inch, details_y - 0.6 * inch, member.id_passport)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(dark_gray)
    c.drawString(6.5 * inch, details_y, "County:")
    c.drawString(6.5 * inch, details_y - 0.3 * inch, "Constituency:")
    c.drawString(6.5 * inch, details_y - 0.6 * inch, "Date Issued:")

    c.setFont("Helvetica", 12)
    c.setFillColor(npv_green)
    c.drawString(8 * inch, details_y, member.county)
    c.drawString(8 * inch, details_y - 0.3 * inch, member.constituency)
    c.drawString(8 * inch, details_y - 0.6 * inch, member.registration_date.strftime("%B %d, %Y"))

    sig_y = height - 7.5 * inch
    c.setStrokeColor(black)
    c.setLineWidth(1)

    c.line(2 * inch, sig_y, 4 * inch, sig_y)
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(3 * inch, sig_y - 0.3 * inch, "Party Secretary General")

    c.line(7 * inch, sig_y, 9 * inch, sig_y)
    c.drawCentredString(8 * inch, sig_y - 0.3 * inch, "Party Leader")

    c.setFont("Helvetica", 9)
    c.setFillColor(dark_gray)
    footer_text = "NPV Plaza 4th Floor, Ruiru By-Pass | +254-771-847-219 | voice@npv.co.ke"
    c.drawCentredString(width / 2, 0.8 * inch, footer_text)

    c.save()

    return f'certificates/{filename}'


def send_certificate_email(member):
    subject = f'NPV Membership Certificate - {member.membership_number}'

    text_content = f"""
Dear {member.get_full_name()},

Congratulations! You are now a registered member of the National People's Voice Party.

Your membership details:
- Membership Number: {member.membership_number}
- Category: {member.membership_category}
- Registration Date: {member.registration_date.strftime("%B %d, %Y")}

Your membership certificate is attached to this email.

Thank you for joining NPV!

Best regards,
National People's Voice Party
"Our Voice, Our Strength"
    """

    email = EmailMessage(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[member.email],
    )

    if member.certificate_file:
        certificate_path = member.certificate_file.path
        if os.path.exists(certificate_path):
            with open(certificate_path, 'rb') as f:
                email.attach(
                    f'NPV_Certificate_{member.membership_number}.pdf',
                    f.read(),
                    'application/pdf'
                )

    try:
        email.send(fail_silently=False)
        member.certificate_sent = True
        member.save()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False