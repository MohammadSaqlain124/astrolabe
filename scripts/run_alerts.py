from dotenv import load_dotenv

from app.alerts.engine import check_and_send_alerts
from app.alerts.notifier import EmailNotifier

load_dotenv()


def main():
    count = check_and_send_alerts(EmailNotifier(), within_hours=24)
    print(f"{count} alert email(s) sent.")


if __name__ == "__main__":
    main()