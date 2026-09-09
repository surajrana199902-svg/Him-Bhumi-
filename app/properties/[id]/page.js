import { Detail, ConciergeAI } from '../../_views'

export default async function PropertyDetailPage({ params }) {
  const { id } = await params
  return (
    <>
      <Detail id={id} />
      <ConciergeAI />
    </>
  )
}
