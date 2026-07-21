import { Metadata } from "next";
import { LoginForm } from "@/features/auth/components/login-form";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your SpeakLift account.",
};

export default function LoginPage() {
  return <LoginForm />;
}
