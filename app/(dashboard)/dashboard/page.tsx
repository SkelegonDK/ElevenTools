import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, Languages, History, Settings } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome to ElevenTools</h1>
        <p className="text-muted-foreground mt-2">
          Developer-focused bulk text-to-speech generation with personalization and translation
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Bulk Generation
            </CardTitle>
            <CardDescription>
              Generate multiple audio files from CSV with variable personalization
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/bulk">
              <Button className="w-full">Get Started</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Languages className="h-5 w-5" />
              Translation
            </CardTitle>
            <CardDescription>
              Translate text before generating audio with OpenRouter models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/translate">
              <Button className="w-full" variant="outline">Translate</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              History
            </CardTitle>
            <CardDescription>
              View and manage your generation history
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/history">
              <Button className="w-full" variant="outline">View History</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Settings
            </CardTitle>
            <CardDescription>
              Configure API keys and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/settings">
              <Button className="w-full" variant="outline">Configure</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
