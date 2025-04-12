from project_root.core.utils import config_loader
print("Script has started.")
def main():
    # Fetch a few config values
    email_user = config_loader.get_config('EMAIL_USER')
    email_password = config_loader.get_config('EMAIL_PASSWORD')
    log_path = config_loader.get_config('LOG_PATH', default='logs/default.log')
    not_present = config_loader.get_config('NOT_PRESENT_KEY', default='default_value')

    # Print to check if values are loaded
    print(f"Email User: {email_user}")
    print(f"Email Password: {email_password}")
    print(f"Log Path: {log_path}")
    print(f"Not Present Key (default): {not_present}")

if __name__ == "__main__":
    main()
