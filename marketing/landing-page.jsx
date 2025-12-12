import React, { useState } from 'react';

// CrewCFO Landing Page - AI Bookkeeping for Roofing Contractors
// Deploy to: Vercel, Netlify, or any React host

const LandingPage = () => {
  const [email, setEmail] = useState('');
  
  const features = [
    {
      icon: "🏷️",
      title: "AI That Knows Roofing",
      description: "Our AI classifies 70%+ of transactions automatically. Home Depot? Materials. Sub payment? Labor. No rules to set up—it just learns your business.",
      stat: "70%+ auto-classified"
    },
    {
      icon: "🏠",
      title: "Know Your Margins. Every Job.",
      description: "See exactly what each job cost—materials, labor, subs, dump fees—and what you actually made. No more 'gut feel' pricing.",
      stat: "Real-time job P&L"
    },
    {
      icon: "📈",
      title: "See 13 Weeks Ahead",
      description: "Our forecasting engine factors in AR, upcoming bills, payroll, and seasonal patterns. Never be surprised by a cash crunch again.",
      stat: "13-week forecast"
    },
    {
      icon: "📋",
      title: "Your CFO in Your Inbox",
      description: "Every Friday, get a plain-English summary: what happened, where you stand, and what to watch. Like a fractional CFO without the $3K/month.",
      stat: "Weekly insights"
    }
  ];

  const painPoints = [
    {
      icon: "📦",
      title: "Drowning in Receipts",
      description: "Your truck console is full of Home Depot receipts. Your email is full of invoices. Your accountant is full of questions."
    },
    {
      icon: "🔮",
      title: "Flying Blind on Cash",
      description: "You finished three jobs last month but you're still scrambling for payroll. Where did the money go?"
    },
    {
      icon: "🎢",
      title: "The Cash Flow Rollercoaster",
      description: "Storm season you're flush. Winter you're stressed. One slow month and you're floating payroll on credit."
    }
  ];

  const testimonials = [
    {
      quote: "I used to spend every Sunday night doing books. Now I check the dashboard Monday morning and I'm done. CrewCFO gave me my weekends back.",
      name: "Jake M.",
      company: "Summit Roofing",
      location: "Denver, CO",
      metric: "4 crews, $2.1M revenue"
    },
    {
      quote: "Last year I almost missed payroll twice. This year I can see three months out. I sleep better knowing exactly where we stand.",
      name: "Maria S.",
      company: "Lone Star Exteriors",
      location: "Austin, TX",
      metric: "6 crews, $3.8M revenue"
    },
    {
      quote: "We were losing money on insurance jobs and didn't even know it. CrewCFO showed us our margins were 8% instead of 25%. We fixed our pricing and added $40K to the bottom line.",
      name: "Tom B.",
      company: "StormPro Roofing",
      location: "Oklahoma City, OK",
      metric: "3 crews, $1.4M revenue"
    }
  ];

  const pricingFeatures = [
    "Unlimited transactions",
    "Unlimited jobs & projects",
    "Unlimited users",
    "AI auto-classification",
    "Job costing & margins",
    "13-week cash forecast",
    "Weekly CFO brief",
    "AR aging & reminders",
    "QuickBooks sync",
    "Mobile dashboard",
    "Email & chat support",
    "Onboarding call included"
  ];

  const faqs = [
    {
      q: "Do I need to be good with computers?",
      a: "If you can use email and QuickBooks, you can use CrewCFO. We handle the technical stuff. Most owners are up and running in under an hour."
    },
    {
      q: "Will this replace my bookkeeper?",
      a: "It depends. Some customers replace their bookkeeper entirely. Others use CrewCFO to make their bookkeeper 3x more efficient. Either way, you'll spend less time on books."
    },
    {
      q: "How does it work with QuickBooks?",
      a: "We sync two-way with QuickBooks Online. Your books stay in QBO—we just make them smarter. Transactions, invoices, and bills flow automatically."
    },
    {
      q: "Is my data secure?",
      a: "Bank-level security. We use 256-bit encryption, SOC 2 compliant infrastructure, and never store your banking credentials."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-slate-950/90 backdrop-blur-sm z-50 border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏠</span>
            <span className="text-xl font-bold">CrewCFO</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm text-slate-400">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
            <a href="#testimonials" className="hover:text-white transition">Testimonials</a>
            <a href="#faq" className="hover:text-white transition">FAQ</a>
          </div>
          <button className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-4 py-2 rounded-lg transition">
            Book Demo
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-block bg-emerald-500/10 text-emerald-400 text-sm font-medium px-3 py-1 rounded-full mb-6">
                Built for Roofing Contractors
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
                Stop Guessing.<br />
                <span className="text-emerald-400">Know Your Cash.</span>
              </h1>
              <p className="text-xl text-slate-400 mb-8 leading-relaxed">
                CrewCFO is the AI-powered finance platform built for roofing contractors. 
                Automated bookkeeping, job costing, and cash forecasting—so you can focus on roofs, not receipts.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-8 py-4 rounded-lg text-lg transition">
                  Book a Free Demo
                </button>
                <button className="border border-slate-600 hover:border-slate-500 text-white font-semibold px-8 py-4 rounded-lg text-lg transition">
                  See How It Works →
                </button>
              </div>
              <div className="flex gap-6 mt-8 text-sm text-slate-500">
                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span> 14-day free trial
                </span>
                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span> No credit card
                </span>
                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span> Setup in 1 hour
                </span>
              </div>
            </div>
            
            {/* Dashboard Preview */}
            <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 shadow-2xl">
              <div className="flex gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              {/* Mini Dashboard */}
              <div className="space-y-4">
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4">
                  <div className="text-emerald-400 text-sm mb-1">Overall Status</div>
                  <div className="text-2xl font-bold flex items-center gap-2">
                    🟢 Healthy
                    <span className="text-sm font-normal text-slate-400">12 weeks runway</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800 rounded-lg p-4">
                    <div className="text-slate-400 text-sm mb-1">Cash Balance</div>
                    <div className="text-2xl font-bold">$127,450</div>
                    <div className="text-emerald-400 text-sm">↑ 8% this week</div>
                  </div>
                  <div className="bg-slate-800 rounded-lg p-4">
                    <div className="text-slate-400 text-sm mb-1">Revenue MTD</div>
                    <div className="text-2xl font-bold">$87,500</div>
                    <div className="text-slate-400 text-sm">88% of target</div>
                  </div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-2">Job Profitability</div>
                  <div className="space-y-2">
                    {[
                      { name: "Smith Residence", margin: 33, amount: "$18,000" },
                      { name: "Johnson Commercial", margin: 38, amount: "$45,000" },
                      { name: "Williams Repair", margin: 18, amount: "$8,500" },
                    ].map((job, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-sm">{job.name}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-slate-400 text-sm">{job.amount}</span>
                          <span className={`text-sm font-medium ${job.margin > 25 ? 'text-emerald-400' : 'text-amber-400'}`}>
                            {job.margin}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pain Points Section */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Running a Roofing Business Is Hard Enough
          </h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            You didn't start a roofing company to become an accountant. But somehow, that's where all your time goes.
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            {painPoints.map((point, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                <div className="text-4xl mb-4">{point.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{point.title}</h3>
                <p className="text-slate-400">{point.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Meet Your AI-Powered Finance Team
          </h2>
          <p className="text-slate-400 mb-16 max-w-2xl mx-auto">
            CrewCFO combines AI bookkeeping with CFO-level insights—built specifically for roofing contractors.
          </p>
          
          {/* How It Works */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            {[
              { step: "1", title: "Connect", desc: "Link QuickBooks and your bank accounts in 5 minutes. We sync automatically." },
              { step: "2", title: "Automate", desc: "Our AI classifies transactions, assigns job costs, and flags exceptions." },
              { step: "3", title: "Know", desc: "Open your dashboard and see cash, margins, and forecast in seconds." }
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="bg-emerald-500 text-black w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-slate-400">{item.desc}</p>
                {i < 2 && (
                  <div className="hidden md:block absolute top-6 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-emerald-500 to-transparent"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Everything You Need. Nothing You Don't.
          </h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            Purpose-built for roofing contractors. Not generic accounting software with a new coat of paint.
          </p>
          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-8 border border-slate-800 hover:border-emerald-500/50 transition">
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{feature.icon}</div>
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold">{feature.title}</h3>
                      <span className="bg-emerald-500/10 text-emerald-400 text-xs px-2 py-1 rounded-full">
                        {feature.stat}
                      </span>
                    </div>
                    <p className="text-slate-400">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Trusted by Roofers Who'd Rather Be Roofing
          </h2>
          <p className="text-slate-400 text-center mb-12">
            Join contractors who've taken control of their finances.
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                <div className="text-emerald-400 text-4xl mb-4">"</div>
                <p className="text-slate-300 mb-6 leading-relaxed">{testimonial.quote}</p>
                <div className="border-t border-slate-800 pt-4">
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-slate-400 text-sm">{testimonial.company} • {testimonial.location}</div>
                  <div className="text-emerald-400 text-sm mt-1">{testimonial.metric}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Simple Pricing. Unlimited Everything.
          </h2>
          <p className="text-slate-400 mb-12">
            One plan. One price. No surprises.
          </p>
          
          <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800 max-w-lg mx-auto">
            <div className="text-emerald-400 font-semibold mb-2">COMPLETE</div>
            <div className="flex items-baseline justify-center gap-2 mb-2">
              <span className="text-5xl font-bold">$299</span>
              <span className="text-slate-400">/month</span>
            </div>
            <div className="text-slate-400 text-sm mb-8">
              or $249/mo billed annually (save $600)
            </div>
            
            <div className="grid grid-cols-2 gap-3 text-left mb-8">
              {pricingFeatures.map((feature, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-slate-300">{feature}</span>
                </div>
              ))}
            </div>
            
            <button className="w-full bg-emerald-500 hover:bg-emerald-400 text-black font-semibold py-4 rounded-lg text-lg transition">
              Start 14-Day Free Trial
            </button>
            <p className="text-slate-500 text-sm mt-4">
              No credit card required. Cancel anytime.
            </p>
          </div>
          
          {/* Comparison */}
          <div className="mt-12 grid md:grid-cols-3 gap-4 text-sm">
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
              <div className="text-slate-400 mb-1">vs. Bookkeeper</div>
              <div className="font-semibold">$500-1,500/mo</div>
              <div className="text-slate-500">+ no forecasting</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
              <div className="text-slate-400 mb-1">vs. Fractional CFO</div>
              <div className="font-semibold">$2,000-5,000/mo</div>
              <div className="text-slate-500">+ limited availability</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
              <div className="text-slate-400 mb-1">vs. Doing it yourself</div>
              <div className="font-semibold">Your sanity</div>
              <div className="text-slate-500">+ your weekends</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                <h3 className="font-semibold text-lg mb-2">{faq.q}</h3>
                <p className="text-slate-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-6 bg-gradient-to-b from-slate-900/50 to-emerald-950/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Stop Guessing?
          </h2>
          <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
            Join roofing contractors who've taken control of their finances. 
            Book a free demo and see your numbers clearly—maybe for the first time.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-8 py-4 rounded-lg text-lg transition">
              Book My Free Demo
            </button>
            <button className="border border-slate-600 hover:border-slate-500 text-white font-semibold px-8 py-4 rounded-lg text-lg transition">
              Start 14-Day Trial
            </button>
          </div>
          <div className="flex justify-center gap-8 mt-8 text-sm text-slate-500">
            <span className="flex items-center gap-2">
              🔒 Bank-level security
            </span>
            <span className="flex items-center gap-2">
              ⭐ 4.9/5 rating
            </span>
            <span className="flex items-center gap-2">
              💬 US-based support
            </span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🏠</span>
                <span className="text-xl font-bold">CrewCFO</span>
              </div>
              <p className="text-slate-400 text-sm">
                AI-powered bookkeeping and CFO insights for roofing contractors.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Integrations</a></li>
                <li><a href="#" className="hover:text-white">Roadmap</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
                <li><a href="#" className="hover:text-white">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-slate-500">
            <p>© 2024 CrewCFO. Built for roofers, by people who get it.</p>
            <div className="flex gap-4 mt-4 md:mt-0">
              <a href="#" className="hover:text-white">LinkedIn</a>
              <a href="#" className="hover:text-white">YouTube</a>
              <a href="#" className="hover:text-white">Facebook</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
