from django.conf import settings
from django.core.mail import send_mail


def get_email_base_template(content_html, subject):
    """Wraps content_html in the AI Learning Hub branded email shell."""
    return f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #161C24; font-family: 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #161C24;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #212B36; border-radius: 16px; overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #00A76F 0%, #007B55 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #FFFFFF; margin: 0; font-size: 24px;">AI Learning Hub</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px; color: #FFFFFF;">
                            {content_html}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 30px; text-align: center; border-top: 1px solid rgba(255,255,255,0.08);">
                            <p style="color: #919EAB; font-size: 12px; margin: 0;">
                                AI Learning Hub &mdash; Deine Lernplattform f&uuml;r AI-Kompetenzen
                            </p>
                            <p style="color: #919EAB; font-size: 11px; margin: 8px 0 0;">
                                Du erh&auml;ltst diese E-Mail weil du auf AI Learning Hub registriert bist.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def _send_html_email(subject, content_html, plaintext, recipient_email):
    """Send an HTML email with plaintext fallback."""
    html_message = get_email_base_template(content_html, subject)
    send_mail(
        subject=subject,
        message=plaintext,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=True,
    )


def _user_email(user):
    """Return user email, or None if not set."""
    return user.email if user.email else None


def _should_send(user):
    """Check if user has email and notifications enabled."""
    email = _user_email(user)
    if not email:
        return False
    if hasattr(user, "profile") and not user.profile.email_notifications:
        return False
    return True


# ── E-Mail Types ──────────────────────────────────────────


def send_welcome_email(user):
    """Welcome email on registration."""
    if not _user_email(user):
        return
    name = user.first_name or user.username
    subject = "Willkommen bei AI Learning Hub!"
    content = f"""\
        <h2 style="color: #00A76F; margin-top: 0;">Hallo {name}!</h2>
        <p style="color: #FFFFFF; font-size: 16px; line-height: 1.6;">
            Willkommen bei AI Learning Hub! Wir freuen uns, dass du dabei bist.
        </p>
        <p style="color: #919EAB; font-size: 14px; line-height: 1.6;">
            Deine Reise in die Welt der K&uuml;nstlichen Intelligenz beginnt jetzt.
            Hier ist was dich erwartet:
        </p>
        <table style="width: 100%; margin: 20px 0;">
            <tr>
                <td style="padding: 12px; background-color: rgba(0,167,111,0.1); border-radius: 8px; text-align: center; width: 33%;">
                    <div style="font-size: 24px;">&#129504;</div>
                    <div style="color: #FFFFFF; font-size: 13px; margin-top: 4px;">4 Lernpfade</div>
                </td>
                <td style="width: 10px;"></td>
                <td style="padding: 12px; background-color: rgba(142,51,255,0.1); border-radius: 8px; text-align: center; width: 33%;">
                    <div style="font-size: 24px;">&#129302;</div>
                    <div style="color: #FFFFFF; font-size: 13px; margin-top: 4px;">AI Tutoren</div>
                </td>
                <td style="width: 10px;"></td>
                <td style="padding: 12px; background-color: rgba(255,193,7,0.1); border-radius: 8px; text-align: center; width: 33%;">
                    <div style="font-size: 24px;">&#127942;</div>
                    <div style="color: #FFFFFF; font-size: 13px; margin-top: 4px;">Achievements</div>
                </td>
            </tr>
        </table>
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:5173" style="background-color: #00A76F; color: #FFFFFF; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                Jetzt starten
            </a>
        </div>"""
    plaintext = (
        f"Hallo {name}! Willkommen bei AI Learning Hub. "
        "Deine AI-Reise beginnt jetzt. Besuche http://localhost:5173"
    )
    _send_html_email(subject, content, plaintext, user.email)


def send_achievement_email(user, achievement):
    """Notification when an achievement is unlocked."""
    if not _should_send(user):
        return
    name = user.first_name or user.username
    subject = f"Achievement freigeschaltet: {achievement.name}!"
    content = f"""\
        <h2 style="color: #8E33FF; margin-top: 0;">Gratulation, {name}!</h2>
        <div style="text-align: center; margin: 25px 0; padding: 30px; background-color: rgba(142,51,255,0.1); border-radius: 12px; border: 1px solid rgba(142,51,255,0.3);">
            <div style="font-size: 48px;">{achievement.icon}</div>
            <h3 style="color: #FFFFFF; margin: 10px 0 5px;">{achievement.name}</h3>
            <p style="color: #919EAB; margin: 0;">{achievement.description}</p>
            <div style="margin-top: 15px; display: inline-block; background-color: #8E33FF; color: #FFFFFF; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;">
                +{achievement.xp_reward} XP
            </div>
        </div>
        <p style="color: #919EAB; text-align: center; font-size: 14px;">
            Weiter so! Entdecke weitere Achievements auf der Plattform.
        </p>"""
    plaintext = (
        f"Gratulation, {name}! Du hast das Achievement "
        f'"{achievement.name}" freigeschaltet (+{achievement.xp_reward} XP).'
    )
    _send_html_email(subject, content, plaintext, user.email)


def send_level_up_email(user, new_level, total_xp):
    """Notification when user reaches a new level."""
    if not _should_send(user):
        return
    name = user.first_name or user.username
    level_titles = {
        1: "Anfaenger",
        2: "Lernender",
        3: "Fortgeschritten",
        4: "Experte",
        5: "Meister",
        6: "Grossmeister",
    }
    title = level_titles.get(new_level, f"Level {new_level}")
    subject = f"Level Up! Du bist jetzt Level {new_level} - {title}!"
    content = f"""\
        <h2 style="color: #FFB020; margin-top: 0;">Level Up!</h2>
        <div style="text-align: center; margin: 25px 0;">
            <div style="display: inline-block; width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #FFB020, #FF8800); line-height: 120px; font-size: 48px; font-weight: bold; color: #FFFFFF;">
                {new_level}
            </div>
            <h3 style="color: #FFFFFF; margin: 15px 0 5px;">{title}</h3>
            <p style="color: #919EAB;">{total_xp} XP gesammelt</p>
        </div>
        <p style="color: #FFFFFF; text-align: center; font-size: 16px;">
            Beeindruckend, {name}! Du w&auml;chst &uuml;ber dich hinaus!
        </p>"""
    plaintext = (
        f"Level Up, {name}! Du bist jetzt Level {new_level} ({title}). "
        f"{total_xp} XP gesammelt."
    )
    _send_html_email(subject, content, plaintext, user.email)


def send_path_completed_email(user, learning_path):
    """Notification when a learning path is fully completed."""
    if not _should_send(user):
        return
    name = user.first_name or user.username
    subject = f"Lernpfad abgeschlossen: {learning_path.title}!"
    content = f"""\
        <h2 style="color: #00A76F; margin-top: 0;">Lernpfad abgeschlossen!</h2>
        <div style="text-align: center; margin: 25px 0; padding: 30px; background-color: rgba(0,167,111,0.1); border-radius: 12px; border: 1px solid rgba(0,167,111,0.3);">
            <div style="font-size: 48px;">{learning_path.icon}</div>
            <h3 style="color: #FFFFFF; margin: 10px 0 5px;">{learning_path.title}</h3>
            <p style="color: #919EAB; margin: 0;">Alle Lektionen abgeschlossen!</p>
        </div>
        <p style="color: #FFFFFF; text-align: center; font-size: 16px;">
            Fantastisch, {name}! Du kannst jetzt dein Zertifikat herunterladen.
        </p>
        <div style="text-align: center; margin: 25px 0;">
            <a href="http://localhost:5173/learn/{learning_path.slug}" style="background-color: #FFB020; color: #161C24; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                Zertifikat herunterladen
            </a>
        </div>"""
    plaintext = (
        f"Fantastisch, {name}! Du hast den Lernpfad "
        f'"{learning_path.title}" abgeschlossen. '
        f"Besuche http://localhost:5173/learn/{learning_path.slug} "
        "fuer dein Zertifikat."
    )
    _send_html_email(subject, content, plaintext, user.email)


def send_streak_reminder_email(user, current_streak):
    """Reminder when a streak is at risk."""
    if not _should_send(user):
        return
    name = user.first_name or user.username
    subject = f"Dein {current_streak}-Tage-Streak ist in Gefahr!"
    content = f"""\
        <h2 style="color: #FF5630; margin-top: 0;">Streak-Warnung!</h2>
        <div style="text-align: center; margin: 25px 0;">
            <div style="font-size: 64px;">&#128293;</div>
            <h3 style="color: #FFFFFF;">{current_streak} Tage Streak</h3>
            <p style="color: #FF5630; font-weight: bold;">Nicht verlieren!</p>
        </div>
        <p style="color: #919EAB; text-align: center; font-size: 14px;">
            Hey {name}, du hast heute noch nicht gelernt.
            Schliesse eine Lektion ab um deinen Streak zu behalten!
        </p>
        <div style="text-align: center; margin: 25px 0;">
            <a href="http://localhost:5173/learn" style="background-color: #FF5630; color: #FFFFFF; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                Jetzt weiterlernen
            </a>
        </div>"""
    plaintext = (
        f"Hey {name}, dein {current_streak}-Tage-Streak ist in Gefahr! "
        "Schliesse eine Lektion ab: http://localhost:5173/learn"
    )
    _send_html_email(subject, content, plaintext, user.email)


# ── Preview helpers ───────────────────────────────────────


def get_preview_html(template_name):
    """Return preview HTML for a given template name. Returns None if unknown."""

    class FakeUser:
        first_name = "Max"
        last_name = "Muster"
        username = "max.muster"
        email = "max@example.com"
        id = 1

    class FakeAchievement:
        name = "Erste Schritte"
        description = "Schliesse deine erste Lektion ab"
        icon = "\U0001F3C6"
        xp_reward = 50

    class FakePath:
        title = "AI Grundlagen"
        icon = "\U0001F9E0"
        slug = "ai-grundlagen"

    templates = {
        "welcome": lambda: _preview_welcome(FakeUser()),
        "achievement": lambda: _preview_achievement(FakeUser(), FakeAchievement()),
        "level-up": lambda: _preview_level_up(FakeUser(), 3, 250),
        "path-completed": lambda: _preview_path_completed(FakeUser(), FakePath()),
        "streak-reminder": lambda: _preview_streak_reminder(FakeUser(), 7),
    }

    builder = templates.get(template_name)
    if not builder:
        return None
    return builder()


def _build_welcome_content(name):
    return f"""\
        <h2 style="color: #00A76F; margin-top: 0;">Hallo {name}!</h2>
        <p style="color: #FFFFFF; font-size: 16px; line-height: 1.6;">
            Willkommen bei AI Learning Hub! Wir freuen uns, dass du dabei bist.
        </p>"""


def _preview_welcome(user):
    name = user.first_name or user.username
    subject = "Willkommen bei AI Learning Hub!"
    content = _build_welcome_content(name)
    return get_email_base_template(content, subject)


def _preview_achievement(user, achievement):
    name = user.first_name or user.username
    subject = f"Achievement freigeschaltet: {achievement.name}!"
    content = f"""\
        <h2 style="color: #8E33FF; margin-top: 0;">Gratulation, {name}!</h2>
        <div style="text-align: center; margin: 25px 0; padding: 30px; background-color: rgba(142,51,255,0.1); border-radius: 12px; border: 1px solid rgba(142,51,255,0.3);">
            <div style="font-size: 48px;">{achievement.icon}</div>
            <h3 style="color: #FFFFFF; margin: 10px 0 5px;">{achievement.name}</h3>
            <p style="color: #919EAB; margin: 0;">{achievement.description}</p>
            <div style="margin-top: 15px; display: inline-block; background-color: #8E33FF; color: #FFFFFF; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;">
                +{achievement.xp_reward} XP
            </div>
        </div>"""
    return get_email_base_template(content, subject)


def _preview_level_up(user, new_level, total_xp):
    name = user.first_name or user.username
    level_titles = {
        1: "Anfaenger", 2: "Lernender", 3: "Fortgeschritten",
        4: "Experte", 5: "Meister", 6: "Grossmeister",
    }
    title = level_titles.get(new_level, f"Level {new_level}")
    subject = f"Level Up! Du bist jetzt Level {new_level} - {title}!"
    content = f"""\
        <h2 style="color: #FFB020; margin-top: 0;">Level Up!</h2>
        <div style="text-align: center; margin: 25px 0;">
            <div style="display: inline-block; width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #FFB020, #FF8800); line-height: 120px; font-size: 48px; font-weight: bold; color: #FFFFFF;">
                {new_level}
            </div>
            <h3 style="color: #FFFFFF; margin: 15px 0 5px;">{title}</h3>
            <p style="color: #919EAB;">{total_xp} XP gesammelt</p>
        </div>
        <p style="color: #FFFFFF; text-align: center; font-size: 16px;">
            Beeindruckend, {name}!</p>"""
    return get_email_base_template(content, subject)


def _preview_path_completed(user, path):
    name = user.first_name or user.username
    subject = f"Lernpfad abgeschlossen: {path.title}!"
    content = f"""\
        <h2 style="color: #00A76F; margin-top: 0;">Lernpfad abgeschlossen!</h2>
        <div style="text-align: center; margin: 25px 0; padding: 30px; background-color: rgba(0,167,111,0.1); border-radius: 12px; border: 1px solid rgba(0,167,111,0.3);">
            <div style="font-size: 48px;">{path.icon}</div>
            <h3 style="color: #FFFFFF; margin: 10px 0 5px;">{path.title}</h3>
            <p style="color: #919EAB; margin: 0;">Alle Lektionen abgeschlossen!</p>
        </div>
        <p style="color: #FFFFFF; text-align: center; font-size: 16px;">
            Fantastisch, {name}!</p>"""
    return get_email_base_template(content, subject)


def _preview_streak_reminder(user, streak):
    name = user.first_name or user.username
    subject = f"Dein {streak}-Tage-Streak ist in Gefahr!"
    content = f"""\
        <h2 style="color: #FF5630; margin-top: 0;">Streak-Warnung!</h2>
        <div style="text-align: center; margin: 25px 0;">
            <div style="font-size: 64px;">&#128293;</div>
            <h3 style="color: #FFFFFF;">{streak} Tage Streak</h3>
            <p style="color: #FF5630; font-weight: bold;">Nicht verlieren!</p>
        </div>
        <p style="color: #919EAB; text-align: center; font-size: 14px;">
            Hey {name}, du hast heute noch nicht gelernt.</p>"""
    return get_email_base_template(content, subject)
