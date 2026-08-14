# GET /api/v1/public/recipes/{slug}/

Detalle de receta publicada. Query: `?lang=es`.

Incluye `has_video` (boolean). El `bunny_video_id` **no** se expone. La URL firmada está en [`GET /me/recipes/{id}/video/`](../me/content.md).

Errores: `404 RECIPE_NOT_FOUND`.
