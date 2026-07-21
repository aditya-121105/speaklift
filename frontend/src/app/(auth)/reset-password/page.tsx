import { Metadata } from "next";
import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";

export const metadata: Metadata = {
  title: "Reset Password",
  description: "Set a new password for your SpeakLift account.",
};

export default function ResetPasswordPage() {
  return <ResetPasswordForm />;
}
