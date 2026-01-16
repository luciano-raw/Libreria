'use client'

import { useState } from 'react'
import { createFirstStore } from '@/server/actions/store'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { useRouter } from 'next/navigation'

export function OnboardingForm() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    const res = await createFirstStore(name)
    if (res.success) {
      router.refresh()
    } else {
      alert(res.message)
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>Bienvenido a LibraryMaster</CardTitle>
          <CardDescription>Para comenzar, crea tu primera librería.</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent>
            <div className="grid w-full items-center gap-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="name">Nombre de la Librería</Label>
                <Input
                  id="name"
                  placeholder="Ej. Librería Central"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button type="submit" disabled={loading}>
              {loading ? 'Creando...' : 'Crear Librería'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
