import { Metadata } from "next";
import { ForgotPasswordForm } from "@/features/auth/components/forgot-password-form";

export const metadata: Metadata = {
  title: "Forgot Password",
  description: "Reset your SpeakLift password.",
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordForm />;
}
