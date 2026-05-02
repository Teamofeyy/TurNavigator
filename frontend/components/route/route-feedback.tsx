'use client'

import { useEffect, useMemo, useState } from 'react'

import { api, ApiError } from '@/lib/api'
import type { FeedbackResponse, Route } from '@/lib/types'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { CheckIcon, LoaderIcon, StarIcon } from '@/components/ui/icons'

interface RouteFeedbackProps {
  route: Route
}

const ratingLabels: Record<number, string> = {
  1: 'Маршрут не подошёл',
  2: 'Слабое попадание',
  3: 'Нормально для MVP',
  4: 'Хороший маршрут',
  5: 'Очень полезно',
}

export function RouteFeedback({ route }: RouteFeedbackProps) {
  const [rating, setRating] = useState<number | null>(null)
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submittedFeedback, setSubmittedFeedback] = useState<FeedbackResponse | null>(null)

  useEffect(() => {
    setRating(null)
    setComment('')
    setError(null)
    setSubmittedFeedback(null)
  }, [route.id])

  const selectedRatingLabel = useMemo(
    () => (rating ? ratingLabels[rating] : 'Оценка пока не выбрана'),
    [rating],
  )

  const handleSubmit = async () => {
    if (!rating) {
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await api.submitFeedback({
        route_id: route.id,
        rating,
        comment: comment.trim() || null,
      })
      setSubmittedFeedback(response)
    } catch (submissionError) {
      if (submissionError instanceof ApiError) {
        setError(submissionError.message)
      } else {
        setError('Не удалось сохранить оценку маршрута.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="border-border/80 shadow-sm">
      <CardHeader className="border-b">
        <CardTitle className="text-lg">Обратная связь по маршруту</CardTitle>
        <CardDescription>
          Эта оценка сохраняется в журнал решений и пригодится для демонстрации
          объяснимости и полезности системы.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5 px-5 py-5">
        <div className="grid gap-2 sm:grid-cols-5">
          {[1, 2, 3, 4, 5].map((value) => {
            const isActive = rating === value

            return (
              <button
                key={value}
                type="button"
                onClick={() => setRating(value)}
                className={cn(
                  'rounded-xl border px-3 py-3 text-left transition-colors',
                  isActive
                    ? 'border-primary bg-primary/8 text-foreground'
                    : 'border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground',
                )}
              >
                <div className="mb-2 flex items-center gap-2">
                  <StarIcon
                    className={cn('h-4 w-4', isActive ? 'text-amber-500' : 'text-muted-foreground')}
                    filled={isActive}
                  />
                  <span className="text-sm font-semibold">{value}</span>
                </div>
                <div className="text-xs leading-snug">{ratingLabels[value]}</div>
              </button>
            )
          })}
        </div>

        <div className="rounded-xl border border-border bg-muted/30 px-4 py-3 text-sm">
          <span className="font-medium text-foreground">Текущая оценка:</span>{' '}
          <span className="text-muted-foreground">{selectedRatingLabel}</span>
        </div>

        <div className="space-y-2">
          <label htmlFor="route-feedback-comment" className="text-sm font-medium text-foreground">
            Комментарий
          </label>
          <Textarea
            id="route-feedback-comment"
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="Например: маршрут хороший, но хочется больше прогулок и меньше музеев."
            className="min-h-24 resize-y"
            maxLength={1000}
          />
          <div className="text-xs text-muted-foreground">
            Комментарий необязателен, но полезен для анализа качества рекомендаций.
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {submittedFeedback && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            <div className="mb-1 flex items-center gap-2 font-medium">
              <CheckIcon className="h-4 w-4" />
              Оценка сохранена
            </div>
            <div>
              Запись #{submittedFeedback.id} добавлена в журнал решений. Оценка: {submittedFeedback.rating}/5.
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-xs text-muted-foreground">
            Для маршрута #{route.id}, {route.route_points.length} точек
          </div>

          <Button
            onClick={handleSubmit}
            disabled={!rating || isSubmitting}
            className="sm:min-w-48"
          >
            {isSubmitting ? (
              <>
                <LoaderIcon className="mr-2 h-4 w-4" />
                Сохранение...
              </>
            ) : (
              'Сохранить оценку'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
