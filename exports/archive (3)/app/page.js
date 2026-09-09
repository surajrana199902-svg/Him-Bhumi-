'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowRight, Building2, Check, ChevronDown, ChevronLeft, ChevronRight, Compass, Instagram, Mail, MapPin, Menu, MessageCircle, Phone, Play, Send, Share2, Sparkles, Trees, X, Upload, Trash2, ShieldCheck, Star, Loader2, FileText, Video, Camera, BadgeCheck, Home as HomeIcon, Copy } from 'lucide-react'

const CATEGORIES = ['Residential plot', 'Commercial plot', 'House', 'Apartment / Flat', 'Villa', 'Commercial property', 'Shop', 'Office', 'Warehouse', 'Agricultural land', 'Other']
const LISTING_TYPES = ['For sale', 'For rent', 'For lease']
const AREA_UNITS = ['sq. ft.', 'sq. yards', 'marla', 'kanal', 'bigha', 'acre']
const HP_DISTRICTS = ['Bilaspur', 'Chamba', 'Hamirpur', 'Kangra', 'Kinnaur', 'Kullu', 'Lahaul & Spiti', 'Mandi', 'Shimla', 'Sirmaur', 'Solan', 'Una']

const BRAND = 'HimBhumi'
const LOGO = 'https://customer-assets-m6fa6gv7.emergentagent.net/job_himalayan-estates-1/artifacts/eidamywr_HImmm.jpeg'
const HERO_IMAGE = 'https://images.unsplash.com/photo-1531932594968-e5e5e9dee95a?auto=format&fit=crop&w=2200&q=90'
const locations = ['Nalagarh', 'Baddi', 'Solan', 'Shimla', 'Kasauli', 'Parwanoo', 'Dharamshala', 'Kangra', 'Palampur', 'Manali', 'Kullu', 'Mandi', 'Hamirpur', 'Bilaspur', 'Una', 'Chamba', 'Nahan', 'Narkanda']

const api = async (path, options) => {
  const response = await fetch(`/api/${path}`, options)
  const data = await response.json()
  if (!response.ok) throw new Error(data?.error || 'Something went wrong')
  return data
}

function Brand({ dark = false }) {
  return <a href="/" aria-label={`${BRAND} home`} className="group flex items-center gap-3.5">
    <span className="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[#f6efe1] shadow-[0_10px_30px_-10px_rgba(10,74,32,.55)] ring-1 ring-[#c9a86a]/80 transition group-hover:ring-[#c9a86a]">
      <img src={LOGO} alt={`${BRAND} Real Estates emblem`} className="h-full w-full object-cover" style={{ transform: 'scale(2.1)', objectPosition: '50% 30%' }} />
      <span className="pointer-events-none absolute inset-0 rounded-full ring-1 ring-inset ring-white/50" />
    </span>
    <span className="flex flex-col leading-none">
      <span className={`font-serif text-[1.55rem] tracking-tight ${dark ? 'text-white' : 'text-foreground'}`}>Him<span className="italic text-[#c9a86a]">Bhumi</span></span>
      <span className="mt-1.5 flex items-center gap-2">
        <span className="h-px w-4 bg-[#c9a86a]/70" />
        <span className={`text-[9.5px] font-semibold uppercase tracking-[0.34em] ${dark ? 'text-white/60' : 'text-muted-foreground'}`}>Real Estates</span>
      </span>
    </span>
  </a>
}

function Header({ dark = false }) {
  return <header className={`absolute inset-x-0 top-0 z-30 ${dark ? 'text-white' : 'text-foreground'}`}>
    <div className="container mx-auto flex h-24 items-center justify-between px-5 lg:px-10">
      <Brand dark={dark} />
      <nav className="hidden items-center gap-8 text-sm font-medium md:flex"><a href="/properties" className="opacity-80 transition hover:opacity-100">Properties</a><a href="/list-your-property" className="opacity-80 transition hover:opacity-100">List property</a><a href="/#story" className="opacity-80 transition hover:opacity-100">Our story</a><a href="/admin" className="opacity-80 transition hover:opacity-100">Admin</a></nav>
      <a href="/list-your-property" className="hidden items-center gap-2 rounded-full border border-current/25 px-5 py-2.5 text-sm transition hover:bg-white/10 md:flex">List your property <ArrowRight size={15} /></a>
      <button className="rounded-full border border-current/25 p-2 md:hidden" aria-label="Open menu"><Menu size={19} /></button>
    </div>
  </header>
}

function Home() {
  const [location, setLocation] = useState('Nalagarh')
  return <main className="bg-background text-foreground">
    <section className="relative flex min-h-[760px] items-end overflow-hidden bg-slate-900 pb-20 text-white lg:min-h-screen lg:items-center lg:pb-0">
      <div className="absolute inset-0"><video autoPlay muted loop playsInline poster={HERO_IMAGE} className="h-full w-full object-cover opacity-80" src="https://cdn.coverr.co/videos/coverr-aerial-view-of-the-mountains-1577/1080p.mp4" /><img src={HERO_IMAGE} alt="Himachal mountain valley" className="absolute inset-0 -z-10 h-full w-full object-cover" /></div>
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(6,23,29,.82),rgba(6,23,29,.32),rgba(6,23,29,.24))]" />
      <Header dark />
      <div className="container relative z-10 mx-auto w-full px-5 lg:px-10"><div className="max-w-3xl"><div className="mb-7 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.3em] text-teal-200"><span className="h-px w-12 bg-teal-300" /> Himachal Pradesh / curated living</div><h1 className="max-w-3xl font-serif text-5xl leading-[0.98] tracking-[-0.04em] sm:text-7xl lg:text-[7.2rem]">Find your dream property <span className="italic text-teal-200">with {BRAND}.</span></h1><p className="mt-7 max-w-lg text-base leading-7 text-white/75 lg:text-lg">Discover premium properties across Himachal Pradesh.</p></div>
        <div className="mt-12 flex max-w-2xl flex-col gap-3 rounded-2xl border border-white/20 bg-white/10 p-3 backdrop-blur-xl sm:flex-row sm:items-center"><div className="flex flex-1 items-center gap-3 rounded-xl bg-black/10 px-4 py-3"><MapPin size={18} className="text-teal-200" /><select value={location} onChange={(event) => setLocation(event.target.value)} className="w-full appearance-none bg-transparent text-sm font-medium text-white outline-none"><option className="text-slate-900">Nalagarh</option>{locations.slice(1).map((item) => <option key={item} className="text-slate-900">{item}</option>)}</select><ChevronDown size={17} className="text-white/60" /></div><a href={`/properties?location=${encodeURIComponent(location)}`} className="flex items-center justify-center gap-3 rounded-xl bg-teal-300 px-6 py-3.5 text-sm font-semibold text-slate-950 transition hover:bg-teal-200">View properties <ArrowRight size={16} /></a></div>
      </div>
    </section>
    <section id="story" className="container mx-auto grid gap-12 px-5 py-24 lg:grid-cols-[.9fr_1.1fr] lg:px-10 lg:py-32"><div><p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">A higher standard</p><h2 className="mt-5 max-w-xl font-serif text-4xl leading-tight tracking-tight sm:text-6xl">Rooted in the <span className="italic text-teal-700">extraordinary.</span></h2></div><div className="max-w-xl self-end"><p className="text-lg leading-8 text-muted-foreground">{BRAND} brings a more thoughtful way to find a home in the hills. From first light over the Dhauladhar to the quiet of a cedar forest, we curate spaces that belong here.</p><a href="/properties" className="mt-8 inline-flex items-center gap-3 border-b border-teal-700 pb-2 text-sm font-semibold text-teal-800">Explore the collection <ArrowRight size={16} /></a></div></section>
    <section className="bg-[#edf2ed] py-20"><div className="container mx-auto grid gap-5 px-5 sm:grid-cols-3 lg:px-10"><div className="rounded-2xl bg-white p-7"><Trees className="text-teal-700" /><p className="mt-12 font-serif text-3xl">The right place</p><p className="mt-3 text-sm leading-6 text-muted-foreground">A location-led collection across Himachal’s most sought-after valleys.</p></div><div className="rounded-2xl bg-teal-900 p-7 text-white"><Sparkles className="text-teal-200" /><p className="mt-12 font-serif text-3xl">The considered choice</p><p className="mt-3 text-sm leading-6 text-white/65">Homes selected for their character, setting, and lasting value.</p></div><div className="rounded-2xl bg-[#d6e3dc] p-7"><Compass className="text-teal-700" /><p className="mt-12 font-serif text-3xl">The {BRAND} way</p><p className="mt-3 text-sm leading-6 text-muted-foreground">Personal guidance from first viewing to the moment you arrive.</p></div></div></section>
    <section className="container mx-auto px-5 py-20 lg:px-10"><div className="relative overflow-hidden rounded-3xl bg-teal-950 px-7 py-14 text-white sm:px-14"><div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-teal-800/40 blur-3xl" /><div className="relative flex flex-col items-start gap-8 lg:flex-row lg:items-center lg:justify-between"><div className="max-w-xl"><p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#e6c887]">Have a property to sell or rent?</p><h2 className="mt-4 font-serif text-4xl leading-tight tracking-tight sm:text-5xl">List your property <span className="italic text-teal-200">with {BRAND}.</span></h2><p className="mt-4 text-base leading-7 text-white/70">Owners, agents and builders — reach thousands of buyers and tenants across Himachal. Free to list, reviewed by our team, live in no time.</p></div><a href="/list-your-property" className="flex shrink-0 items-center gap-3 rounded-full bg-[#c9a86a] px-7 py-4 text-sm font-semibold text-slate-950 transition hover:bg-[#d9bc82]">List your property <ArrowRight size={16} /></a></div></div></section>
    <Footer />
  </main>
}

function Footer() { return <footer className="bg-slate-950 px-5 py-12 text-white lg:px-10"><div className="container mx-auto flex flex-col justify-between gap-8 md:flex-row md:items-end"><div><Brand dark /><p className="mt-4 max-w-xs text-sm leading-6 text-white/50">Premium property, thoughtfully found in Himachal Pradesh.</p></div><div className="flex items-center gap-5 text-white/50"><a href="/list-your-property" className="text-xs transition hover:text-white">List property</a><a href="/track" className="text-xs transition hover:text-white">Track listing</a><Instagram size={18} /><Mail size={18} /><span className="text-xs">© 2026 {BRAND}</span></div></div></footer> }

function PropertyCard({ property }) { return <a href={`/properties/${property.id}`} className="group block"><div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-muted"><img src={property.image} alt={property.title} className="h-full w-full object-cover transition duration-700 group-hover:scale-105" /><div className="absolute inset-0 bg-gradient-to-t from-slate-950/55 via-transparent to-transparent" /><span className="absolute left-4 top-4 rounded-full border border-white/30 bg-black/15 px-3 py-1 text-[11px] font-medium text-white backdrop-blur-md">{property.type}</span>{property.featured && <span className="absolute right-4 top-4 flex items-center gap-1 rounded-full bg-[#c9a86a] px-2.5 py-1 text-[10px] font-semibold text-slate-900"><Star size={11} /> Featured</span>}<span className="absolute bottom-4 left-4 flex items-center gap-1.5 text-xs text-white/85"><MapPin size={12} /> {property.location}</span></div><div className="flex items-start justify-between gap-4 pt-4"><div><h3 className="flex items-center gap-1.5 font-serif text-2xl tracking-tight">{property.title}{property.verified && <BadgeCheck size={16} className="text-teal-700" />}</h3><p className="mt-1 text-sm text-muted-foreground">{property.area} · {property.address?.split(',')[0]}</p></div><p className="whitespace-nowrap text-sm font-semibold text-teal-800">{property.price}</p></div></a> }

function Properties() {
  const [properties, setProperties] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const [location, setLocation] = useState('All locations')
  useEffect(() => { const selected = new URLSearchParams(window.location.search).get('location'); if (selected) setLocation(selected) }, [])
  useEffect(() => { setLoading(true); api(`properties${location !== 'All locations' ? `?location=${encodeURIComponent(location)}` : ''}`).then((data) => setProperties(data.properties || [])).catch((reason) => setError(reason.message)).finally(() => setLoading(false)) }, [location])
  return <main className="min-h-screen bg-background text-foreground"><div className="border-b border-border bg-[#edf2ed]"><div className="container mx-auto px-5 lg:px-10"><Header /><div className="relative flex min-h-[380px] items-end pb-12 pt-28"><div><p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">The collection</p><h1 className="mt-4 font-serif text-5xl tracking-tight sm:text-7xl">Properties <span className="italic text-teal-700">available in</span></h1><div className="relative mt-7 inline-flex items-center gap-3 rounded-full border border-border bg-white px-4 py-2.5"><MapPin size={16} className="text-teal-700" /><select value={location} onChange={(event) => setLocation(event.target.value)} className="appearance-none bg-transparent pr-8 text-sm font-medium outline-none"><option>All locations</option>{locations.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={15} className="pointer-events-none absolute right-4 text-muted-foreground" /></div></div></div></div></div><div className="container mx-auto px-5 py-14 lg:px-10"><div className="mb-8 flex items-center justify-between"><p className="text-sm text-muted-foreground">{loading ? 'Finding your next address...' : `${properties.length} curated ${properties.length === 1 ? 'property' : 'properties'}`}</p><a href="/" className="text-sm font-medium text-teal-800">Back home</a></div>{error ? <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800">{error}</div> : loading ? <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-3"><div className="aspect-[4/3] animate-pulse rounded-2xl bg-muted" /><div className="aspect-[4/3] animate-pulse rounded-2xl bg-muted" /><div className="aspect-[4/3] animate-pulse rounded-2xl bg-muted" /></div> : properties.length ? <div className="grid gap-x-6 gap-y-12 md:grid-cols-2 lg:grid-cols-3">{properties.map((property) => <PropertyCard key={property.id} property={property} />)}</div> : <div className="rounded-2xl border border-dashed border-border py-24 text-center"><p className="font-serif text-3xl">A quieter corner awaits.</p><p className="mt-2 text-sm text-muted-foreground">We are curating new properties in this location.</p></div>}</div></main>
}

function Detail({ id }) {
  const [property, setProperty] = useState(null); const [activeImage, setActiveImage] = useState(0); const [form, setForm] = useState({ fullName: '', mobile: '', email: '', message: '', intent: 'buy' }); const [status, setStatus] = useState('')
  useEffect(() => { api(`properties/${id}`).then((data) => setProperty(data)).catch(() => setProperty({ error: true })) }, [id])
  const gallery = property?.gallery?.length ? property.gallery : property?.image ? [property.image] : []
  const submit = async (event) => { event.preventDefault(); setStatus('sending'); try { await api('inquiries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, propertyId: id, propertyTitle: property.title }) }); setStatus('sent'); setForm({ fullName: '', mobile: '', email: '', message: '', intent: 'buy' }) } catch (reason) { setStatus(reason.message) } }
  if (!property) return <div className="flex min-h-screen items-center justify-center bg-background"><div className="h-8 w-8 animate-spin rounded-full border-2 border-teal-700 border-t-transparent" /></div>
  if (property.error) return <div className="flex min-h-screen flex-col items-center justify-center gap-4"><p className="font-serif text-3xl">Property not found</p><a href="/properties" className="text-teal-800">Return to collection</a></div>
  return <main className="bg-background text-foreground"><div className="container mx-auto px-5 lg:px-10"><div className="relative pt-24"><a href="/properties" className="mb-8 inline-flex items-center gap-2 text-sm text-muted-foreground transition hover:text-foreground"><ChevronLeft size={16} /> Back to collection</a><div className="grid gap-2 overflow-hidden rounded-2xl md:grid-cols-[1.35fr_.65fr]"><div className="relative aspect-[4/3] md:aspect-auto md:min-h-[580px]"><img src={gallery[activeImage]} alt={property.title} className="h-full w-full object-cover" /><button onClick={() => setActiveImage((activeImage + gallery.length - 1) % gallery.length)} className="absolute left-4 top-1/2 rounded-full bg-white/85 p-2 backdrop-blur" aria-label="Previous image"><ChevronLeft size={18} /></button><button onClick={() => setActiveImage((activeImage + 1) % gallery.length