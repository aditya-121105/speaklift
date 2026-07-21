import { Metadata } from "next";
import { SignupForm } from "@/features/auth/components/signup-form";

export const metadata: Metadata = {
  title: "Sign Up",
  description: "Create your SpeakLift account.",
};

export default function SignupPage() {
  return <SignupForm />;
}
