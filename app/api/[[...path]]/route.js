import { NextResponse } from 'next/server'
import { randomUUID } from 'crypto'
import { MongoClient } from 'mongodb'

let clientPromise
const images = [
  'https://images.unsplash.com/photo-1759123136466-63b3c37db41f?auto=format&fit=crop&w=1400&q=85',
  'https://images.unsplash.com/photo-1767634854859-db8255389e64?auto=format&fit=crop&w=1400&q=85',
  'https://images.unsplash.com/photo-1780391592801-5e8867523492?auto=format&fit=crop&w=1400&q=85',
  'https://images.unsplash.com/photo-1589891685391-b37508e8df4c?auto=format&fit=crop&w=1400&q=85',
  'https://images.unsplash.com/photo-1531932594968-e5e5e9dee95a?auto=format&fit=crop&w=1400&q=85',
]
const locations = ['Nalagarh', 'Baddi', 'Solan', 'Shimla', 'Kasauli', 'Parwanoo', 'Dharamshala', 'Kangra', 'Palampur', 'Manali', 'Kullu', 'Mandi', 'Hamirpur', 'Bilaspur', 'Una', 'Chamba', 'Nahan', 'Narkanda']
const starterProperties = [
  { title: 'The Cedar House', location: 'Kasauli', price: '₹ 4.85 Cr', type: 'Villa', area: '3,200 sq. ft.', address: 'Manki Point Road, Kasauli, Himachal Pradesh', image: images[0], gallery: [images[0], images[1], images[2]], description: 'A considered mountain residence where warm cedar, generous glazing, and quiet outdoor spaces frame the best of Kasauli. Designed for slow weekends and effortless hosting.', amenities: ['Mountain views', 'Private garden', 'Fireplace lounge', 'Solar backup', 'Staff room'], specs: [{ label: 'Bedrooms', value: '4' }, { label: 'Bathrooms', value: '4.5' }, { label: 'Plot size', value: '8,900 sq. ft.' }, { label: 'Year built', value: '2023' }], nearby: ['Kasauli Club · 8 min', 'Lawrence School · 14 min', 'Kasauli Market · 10 min', 'Gilbert Trail · 12 min'], video: 'https://cdn.coverr.co/videos/coverr-aerial-view-of-the-mountains-1577/1080p.mp4' },
  { title: 'Pinecrest Estate', location: 'Shimla', price: '₹ 7.20 Cr', type: 'Estate', area: '5,850 sq. ft.', address: 'Mashobra Road, Shimla, Himachal Pradesh', image: images[1], gallery: [images[1], images[4], images[0]], description: 'A private estate above Shimla with layered lawns, forest-facing rooms, and a distinctly residential sense of arrival. A rare long-term base in the hills.', amenities: ['Forest outlook', 'Double-height living', 'Home office', 'Covered parking', 'Guest suite'], specs: [{ label: 'Bedrooms', value: '5' }, { label: 'Bathrooms', value: '5' }, { label: 'Plot size', value: '1.4 acres' }, { label: 'Year built', value: '2022' }], nearby: ['Theog Market · 16 min', 'Bishop Cotton School · 24 min', 'IGMC Shimla · 22 min', 'Craignano Nature Park · 8 min'] },
  { title: 'Valley Light Residence', location: 'Dharamshala', price: '₹ 3.40 Cr', type: 'Residence', area: '2,480 sq. ft.', address: 'Naddi Village, Dharamshala, Himachal Pradesh', image: images[3], gallery: [images[3], images[4], images[2]], description: 'A light-filled modern home with long valley views toward the Dhauladhar range. Natural materials and simple planning make every room feel connected to the landscape.', amenities: ['Dhauladhar views', 'Terrace garden', 'Library nook', 'Rainwater harvesting', 'Furnished'], specs: [{ label: 'Bedrooms', value: '3' }, { label: 'Bathrooms', value: '3' }, { label: 'Plot size', value: '5,200 sq. ft.' }, { label: 'Year built', value: '2024' }], nearby: ['Naddi Market · 5 min', 'Tibetan Children’s Village · 13 min', 'Zonal Hospital · 18 min', 'Dal Lake · 6 min'] },
  { title: 'Apple Orchard Retreat', location: 'Manali', price: '₹ 5.65 Cr', type: 'Farmhouse', area: '4,100 sq. ft.', address: 'Prini Village, Manali, Himachal Pradesh', image: images[4], gallery: [images[4], images[2], images[3]], description: 'A quiet orchard retreat near Manali, balancing alpine character with contemporary comfort. The landscape is the hero, with private corners for every season.', amenities: ['Apple orchard', 'Mountain deck', 'Caretaker cottage', 'Wood-fired sauna', 'River access'], specs: [{ label: 'Bedrooms', value: '4' }, { label: 'Bathrooms', value: '4' }, { label: 'Land', value: '1.1 acres' }, { label: 'Year built', value: '2021' }], nearby: ['Old Manali · 12 min', 'The Manali School · 9 min', 'Civil Hospital · 15 min', 'Hadimba Temple · 14 min'] },
  { title: 'The Green Valley Plot', location: 'Baddi', price: '₹ 1.18 Cr', type: 'Land', area: '12,500 sq. ft.', address: 'Bhatoli Kalan, Baddi, Himachal Pradesh', image: images[2], gallery: [images[2], images[3], images[1]], description: 'A well-positioned parcel in the Baddi–Nalagarh growth corridor, suited to a private residence, boutique retreat, or considered investment.', amenities: ['Road frontage', 'Clear title', 'Water connection', 'Electricity nearby', 'Flexible zoning'], specs: [{ label: 'Land area', value: '12,500 sq. ft.' }, { label: 'Road width', value: '30 ft.' }, { label: 'Slope', value: 'Gentle' }, { label: 'Title', value: 'Clear' }], nearby: ['Baddi Market · 9 min', 'Eicher School · 12 min', 'ESI Hospital · 15 min', 'Pinjore Gardens · 28 min'] },
  { title: 'Solan Courtyard Home', location: 'Solan', price: '₹ 2.75 Cr', type: 'Home', area: '2,900 sq. ft.', address: 'Chambaghat, Solan, Himachal Pradesh', image: images[0], gallery: [images[0], images[3], images[4]], description: 'A gracious courtyard home in Solan with a welcoming plan, excellent natural light, and room to grow into a family legacy.', amenities: ['Central courtyard', 'Modular kitchen', 'Study room', 'Garage', 'Solar water heater'], specs: [{ label: 'Bedrooms', value: '4' }, { label: 'Bathrooms', value: '3' }, { label: 'Plot size', value: '6,500 sq. ft.' }, { label: 'Year built', value: '2020' }], nearby: ['Solan Mall · 8 min', 'St. Luke’s School · 10 min', 'Regional Hospital · 11 min', 'Mohan Park · 6 min'] },
]

async function getDb() {
  if (!process.env.MONGO_URL) throw new Error('MONGO_URL is not configured')
  if (!clientPromise) clientPromise = MongoClient.connect(process.env.MONGO_URL)
  const client = await clientPromise
  return client.db(process.env.DB_NAME)
}

function serialize(property) {
  if (!property) return property
  const { _id, ...safe } = property
  return safe
}

async function ensureSeed(db) {
  const collection = db.collection('properties')
  if (await collection.countDocuments() === 0) {
    await collection.insertMany(starterProperties.map((property) => ({ ...property, id: randomUUID(), status: 'published', createdAt: new Date().toISOString() })))
  }
}

function response(data, status = 200) { return NextResponse.json(data, { status }) }

export async function GET(request, { params }) {
  try {
    const db = await getDb()
    const routeParams = await params
    const parts = routeParams?.path || []
    if (parts[0] === 'locations') return response({ locations })
    if (parts[0] === 'properties') {
      await ensureSeed(db)
      if (parts[1]) {
        const property = await db.collection('properties').findOne({ id: parts[1] })
        return property ? response(serialize(property)) : response({ error: 'Property not found' }, 404)
      }
      const selected = new URL(request.url).searchParams.get('location')
      const query = selected && selected !== 'All locations' ? { location: selected } : {}
      const results = await db.collection('properties').find(query).sort({ createdAt: -1 }).toArray()
      return response({ properties: results.map(serialize), locations })
    }
    if (parts[0] === 'inquiries') {
      const inquiries = await db.collection('inquiries').find({}).sort({ createdAt: -1 }).toArray()
      return response({ inquiries: inquiries.map(serialize) })
    }
    return response({ error: 'Route not found' }, 404)
  } catch (error) { return response({ error: error?.message || 'Server error' }, 500) }
}

export async function POST(request, { params }) {
  try {
    const db = await getDb()
    const routeParams = await params
    const parts = routeParams?.path || []
    const body = await request.json()
    if (parts[0] === 'inquiries') {
      if (!body.fullName || !body.mobile || !body.propertyId) return response({ error: 'Name, mobile, and property are required' }, 400)
      const inquiry = { id: randomUUID(), ...body, createdAt: new Date().toISOString(), status: 'new' }
      await db.collection('inquiries').insertOne(inquiry)
      return response({ inquiry: serialize(inquiry) }, 201)
    }
    if (parts[0] === 'properties') {
      if (!body.title || !body.location || !body.price) return response({ error: 'Title, location, and price are required' }, 400)
      const property = { id: randomUUID(), ...body, gallery: body.gallery || [body.image].filter(Boolean), createdAt: new Date().toISOString(), status: body.status || 'published' }
      await db.collection('properties').insertOne(property)
      return response({ property: serialize(property) }, 201)
    }
    return response({ error: 'Route not found' }, 404)
  } catch (error) { return response({ error: error?.message || 'Server error' }, 500) }
}

export async function PUT(request, { params }) {
  try {
    const db = await getDb()
    const routeParams = await params
    const parts = routeParams?.path || []
    if (parts[0] !== 'properties' || !parts[1]) return response({ error: 'Route not found' }, 404)
    const body = await request.json()
    const { id, _id, ...updates } = body
    const result = await db.collection('properties').updateOne({ id: parts[1] }, { $set: { ...updates, updatedAt: new Date().toISOString() } })
    return result.matchedCount ? response({ property: serialize({ ...body, id: parts[1] }) }) : response({ error: 'Property not found' }, 404)
  } catch (error) { return response({ error: error?.message || 'Server error' }, 500) }
}

export async function DELETE(request, { params }) {
  try {
    const db = await getDb()
    const routeParams = await params
    const parts = routeParams?.path || []
    if (parts[0] !== 'properties' || !parts[1]) return response({ error: 'Route not found' }, 404)
    const result = await db.collection('properties').deleteOne({ id: parts[1] })
    return result.deletedCount ? response({ success: true }) : response({ error: 'Property not found' }, 404)
  } catch (error) { return response({ error: error?.message || 'Server error' }, 500) }
}