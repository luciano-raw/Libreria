import { SignIn } from '@clerk/nextjs'
import { AuthLayout } from '@/components/auth-layout'

export default function Page() {
    return (
        <AuthLayout>
            <div className="flex flex-col space-y-4 text-center mb-6">
                <h2 className="text-2xl font-bold tracking-tight text-white">Bienvenido de nuevo</h2>
                <p className="text-sm text-zinc-400">Ingresa tus credenciales para acceder a tu cuenta.</p>
            </div>
            <SignIn
                appearance={{
                    elements: {
                        rootBox: "w-full",
                        card: "bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 shadow-2xl w-full",
                        headerTitle: "hidden",
                        headerSubtitle: "hidden",
                        formButtonPrimary: 'bg-indigo-600 hover:bg-indigo-700 text-white transition-all',
                        footerActionLink: 'text-indigo-400 hover:text-indigo-300',
                        socialButtonsBlockButton: 'bg-zinc-800 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:text-white',
                        socialButtonsBlockButtonText: 'text-zinc-300',
                        dividerLine: 'bg-zinc-800',
                        dividerText: 'text-zinc-500',
                        formFieldLabel: 'text-zinc-400',
                        formFieldInput: 'bg-zinc-950/80 border-zinc-800 text-white placeholder:text-zinc-600 focus:border-indigo-500 transition-colors',
                        identityPreviewText: 'text-zinc-300',
                        identityPreviewEditButton: 'text-indigo-400 hover:text-indigo-300'
                    }
                }}
            />
        </AuthLayout>
    )
}
