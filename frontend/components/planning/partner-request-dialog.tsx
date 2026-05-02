'use client'

import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

type PartnerFormState = {
  venueName: string
  city: string
  category: string
  contact: string
  comment: string
}

const emptyForm: PartnerFormState = {
  venueName: '',
  city: '',
  category: '',
  contact: '',
  comment: '',
}

export function PartnerRequestDialog({ defaultCityName }: { defaultCityName: string }) {
  const [open, setOpen] = useState(false)
  const [submittedCount, setSubmittedCount] = useState(0)
  const [form, setForm] = useState<PartnerFormState>(emptyForm)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleOpenChange = (nextOpen: boolean) => {
    setOpen(nextOpen)
    if (nextOpen) {
      setIsSubmitted(false)
      setForm({
        ...emptyForm,
        city: defaultCityName,
      })
    }
  }

  const handleSubmit = () => {
    setSubmittedCount((count) => count + 1)
    setIsSubmitted(true)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="shrink-0">
          Стать партнёром
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Заявка партнёра</DialogTitle>
          <DialogDescription>
            Пока сохраняем заявку локально в интерфейсе. Этого достаточно для демо-потока и
            последующего подключения backend.
          </DialogDescription>
        </DialogHeader>

        {isSubmitted ? (
          <div className="space-y-4">
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-4 text-sm text-emerald-800">
              <div className="mb-1 font-semibold">Заявка принята</div>
              <div>
                Место <strong>{form.venueName}</strong> добавлено в локальный список заявок.
                Номер в текущей сессии: #{submittedCount}.
              </div>
            </div>

            <div className="rounded-xl border border-stone-200 bg-stone-50 px-4 py-4 text-sm text-stone-700">
              <div className="mb-2 font-medium text-stone-900">Что мы сохранили</div>
              <div>Город: {form.city || 'Не указан'}</div>
              <div>Категория: {form.category || 'Не указана'}</div>
              <div>Контакт: {form.contact || 'Не указан'}</div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="partner-venue-name">Название места</Label>
              <Input
                id="partner-venue-name"
                value={form.venueName}
                onChange={(event) => setForm((prev) => ({ ...prev, venueName: event.target.value }))}
                placeholder="Например: Riverside Coffee"
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="partner-city">Город</Label>
                <Input
                  id="partner-city"
                  value={form.city}
                  onChange={(event) => setForm((prev) => ({ ...prev, city: event.target.value }))}
                  placeholder="Ростов-на-Дону"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="partner-category">Категория</Label>
                <Input
                  id="partner-category"
                  value={form.category}
                  onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))}
                  placeholder="Кафе, музей, отель..."
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="partner-contact">Контакт</Label>
              <Input
                id="partner-contact"
                value={form.contact}
                onChange={(event) => setForm((prev) => ({ ...prev, contact: event.target.value }))}
                placeholder="Почта, телефон или Telegram"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="partner-comment">Комментарий</Label>
              <Textarea
                id="partner-comment"
                value={form.comment}
                onChange={(event) => setForm((prev) => ({ ...prev, comment: event.target.value }))}
                placeholder="Коротко расскажите, чем место полезно для туристического маршрута."
                className="min-h-28 resize-y"
              />
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Закрыть
          </Button>
          {!isSubmitted && (
            <Button onClick={handleSubmit} disabled={!form.venueName || !form.contact}>
              Отправить заявку
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
