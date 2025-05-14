import re
from .firebase_config import auth, admin_auth


class FirebaseAuthHandler:
    @staticmethod
    def validate_password(password):
        """Password must be at least 8 characters with 1 uppercase, 1 lowercase, 1 number"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            return False, "Please enter a valid email address"
        return True, "Email is valid"

    @staticmethod
    def sign_up(username, email, password, confirm_password):
        try:
            # Validate input
            if not username or len(username) < 3:
                return {
                    "success": False,
                    "error": "Username must be at least 3 characters long",
                }

            email_valid, email_msg = FirebaseAuthHandler.validate_email(email)
            if not email_valid:
                return {"success": False, "error": email_msg}

            if password != confirm_password:
                return {"success": False, "error": "Passwords do not match"}

            pass_valid, pass_msg = FirebaseAuthHandler.validate_password(password)
            if not pass_valid:
                return {"success": False, "error": pass_msg}

            # Create user
            user = auth.create_user_with_email_and_password(email, password)

            # Update profile
            auth.update_profile(user["idToken"], display_name=username)
            # Send verification email
            auth.send_email_verification(user["idToken"])

            return {
                "success": True,
                "message": "Account created successfully! Please check your email to verify your account before logging in.",
                "user": user,
            }
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                return {"success": False, "error": "This email is already registered"}
            return {"success": False, "error": f"Registration failed: {error_message}"}

    @staticmethod
    def sign_in(email, password):
        try:
            user_creds = auth.sign_in_with_email_and_password(email, password)
            user_info = auth.get_account_info(user_creds["idToken"])
            if not user_info["users"][0]["emailVerified"]:
                # Optionally, resend verification email if needed or just inform
                # auth.send_email_verification(user_creds['idToken'])
                return {
                    "success": False,
                    "error": "Email not verified. Please check your inbox for a verification email.",
                }
            return {"success": True, "message": "Welcome back!", "user": user_creds}
        except Exception as e:
            error_message = str(e)
            if "INVALID_PASSWORD" in error_message:
                return {"success": False, "error": "Incorrect password"}
            elif "EMAIL_NOT_FOUND" in error_message:
                return {"success": False, "error": "Email not registered"}
            return {"success": False, "error": "Login failed. Please try again."}

    @staticmethod
    def sign_in_with_google(credential_token):
        """Handle Google Sign-in using OAuth credentials"""
        try:
            # Sign in with credential token from client-side Google Sign-in
            user = auth.sign_in_with_credential(credential_token)

            # Get user info from Firebase Auth
            user_info = auth.get_account_info(user["idToken"])

            # Check email verification
            if user_info["users"][0]["emailVerified"]:
                return {
                    "success": True,
                    "message": "Signed in with Google successfully!",
                    "user": {
                        "email": user_info["users"][0]["email"],
                        "displayName": user_info["users"][0].get("displayName"),
                        "photoURL": user_info["users"][0].get("photoUrl"),
                        "idToken": user["idToken"],
                        "uid": user_info["users"][0]["localId"],
                    },
                }
            else:
                return {"success": False, "error": "Google account email not verified"}
        except Exception as e:
            error_msg = str(e)
            if "INVALID_IDP_RESPONSE" in error_msg:
                return {
                    "success": False,
                    "error": "Invalid Google sign-in response. Please try again.",
                }
            elif "USER_DISABLED" in error_msg:
                return {
                    "success": False,
                    "error": "This user account has been disabled.",
                }
            else:
                return {
                    "success": False,
                    "error": f"Google sign-in failed: {error_msg}",
                }

    @staticmethod
    def sign_out():
        try:
            auth.current_user = None
            return {"success": True, "message": "Logged out successfully!"}
        except Exception as e:
            return {"success": False, "error": f"Logout failed: {str(e)}"}

    @staticmethod
    def get_current_user():
        try:
            return auth.current_user
        except Exception:
            return None

    @staticmethod
    def reset_password(email):
        try:
            auth.send_password_reset_email(email)
            return {
                "success": True,
                "message": "Password reset email sent! Please check your inbox.",
            }
        except Exception as e:
            error_message = str(e)
            if "EMAIL_NOT_FOUND" in error_message:
                return {"success": False, "error": "Email not registered"}
            return {
                "success": False,
                "error": "Failed to send reset email. Please try again.",
            }

    @staticmethod
    def sign_in_with_phone(phone_number, verification_id, verification_code):
        """Placeholder for phone number sign-in. Requires Firebase Phone Auth setup."""
        # This is a simplified placeholder. Real implementation involves:
        # 1. Sending an OTP to the phone_number (client-side or server-side via Admin SDK).
        #    auth.send_sign_in_link_to_email(email, action_code_settings) is for email, phone is different.
        #    For phone, you'd typically use firebase.auth().signInWithPhoneNumber(phoneNumber, appVerifier) on client-side
        #    or Admin SDK to manage users by phone.
        # 2. Verifying the OTP (verification_code with verification_id).
        #    credential = firebase.auth.PhoneAuthProvider.credential(verificationId, verificationCode);
        #    auth.sign_in_with_credential(credential)
        try:
            # Example: Using Admin SDK to get user by phone (if already created)
            # user = admin_auth.get_user_by_phone_number(phone_number)
            # Or, if verifying a code from client-side flow:
            # decoded_token = admin_auth.verify_id_token(id_token_from_client_after_phone_auth)
            # uid = decoded_token['uid']
            # user = auth.get_account_info(id_token_from_client_after_phone_auth) # if using client SDK token
            return {
                "success": False,
                "error": "Phone sign-in not fully implemented. Requires Firebase Phone Auth setup and client-side OTP flow.",
            }
        except Exception as e:
            return {"success": False, "error": f"Phone sign-in failed: {str(e)}"}

    @staticmethod
    def verify_email(token):
        """Verify email address using token"""
        try:
            auth.confirm_email_verification(token)
            return {"success": True, "message": "Email verified successfully!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def refresh_token(refresh_token):
        """Refresh the user's authentication token"""
        try:
            user = auth.refresh(refresh_token)
            return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_user_profile(id_token):
        """Get detailed user profile information"""
        try:
            user_info = auth.get_account_info(id_token)
            user = user_info["users"][0]
            return {
                "success": True,
                "profile": {
                    "email": user.get("email"),
                    "emailVerified": user.get("emailVerified", False),
                    "displayName": user.get("displayName"),
                    "photoURL": user.get("photoUrl"),
                    "providers": [
                        p.get("providerId") for p in user.get("providerUserInfo", [])
                    ],
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_user_profile(id_token, display_name=None, photo_url=None):
        """Update user profile information"""
        try:
            update_data = {}
            if display_name:
                update_data["displayName"] = display_name
            if photo_url:
                update_data["photoURL"] = photo_url

            user = auth.update_profile(id_token, **update_data)
            return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def check_auth_state():
        """Check current authentication state"""
        try:
            current_user = auth.current_user
            if current_user:
                user_info = auth.get_account_info(current_user["idToken"])
                return {
                    "success": True,
                    "authenticated": True,
                    "user": user_info["users"][0],
                }
            return {"success": True, "authenticated": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
