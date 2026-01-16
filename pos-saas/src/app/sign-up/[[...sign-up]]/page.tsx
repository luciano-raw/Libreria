import { SignUp } from '@clerk/nextjs'

export default function Page() {
    return (
        <div className="flex min-h-screen w-full items-center justify-center bg-zinc-950 px-4">
            <div className="w-full max-w-md space-y-8">
                <div className="flex flex-col items-center">
                    <div className="h-10 w-10 rounded-xl bg-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-900/40 mb-4">
                        LM
                    </div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Crear Cuenta</h2>
                    <p className="text-zinc-400">Comienza a gestionar tu librería hoy</p>
                </div>
                <div className="flex justify-center">
                    <SignUp
                        appearance={{
                            elements: {
                                formButtonPrimary: 'bg-purple-600 hover:bg-purple-700 text-white',
                                footerActionLink: 'text-purple-400 hover:text-purple-300',
                                card: 'bg-zinc-900 border border-zinc-800 shadow-xl',
                                headerTitle: 'hidden',
                                headerSubtitle: 'hidden',
                                socialButtonsBlockButton: 'bg-zinc-800 border-zinc-700 text-zinc-300 hover:bg-zinc-700',
                                socialButtonsBlockButtonText: 'text-zinc-300',
                                dividerLine: 'bg-zinc-700',
                                dividerText: 'text-zinc-500',
                                formFieldLabel: 'text-zinc-400',
                                formFieldInput: 'bg-zinc-950 border-zinc-700 text-white placeholder:text-zinc-600',
                                identityPreviewText: 'text-zinc-300',
                                identityPreviewEditButton: 'text-purple-400 hover:text-purple-300'
                            }
                        }}
                    />
                </div>
            </div>
        </div>
    )
}
