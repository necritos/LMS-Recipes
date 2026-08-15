# GET /api/v1/public/recipes/{slug}/

Detalle de receta publicada. Query: `?lang=es`.

Incluye `has_video` (boolean). El `bunny_video_id` **no** se expone.  
`ingredients_html` y `preparation_html` **tampoco** (solo tras compra: [`GET /me/recipes/{id}/`](../me/content.md)).

Errores: `404 RECIPE_NOT_FOUND`.
