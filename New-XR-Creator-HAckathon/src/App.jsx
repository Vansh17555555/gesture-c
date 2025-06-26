import React from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import FAQ from './components/FAQ';
import Theme from './components/Theme';
import './App.css';
import About from './components/About';
import Timelines from './components/Timeline';
import Prize from './components/Prize';
import Organiser from './components/Organiser';
import Waves from './components/Waves';
import { Section } from 'lucide-react';

const App = () => {
  const register = () => {
    alert(
      "We're excited to announce that registrations will begin on 10th September. Mark your calendars and stay tuned for updates. We can't wait to see you join us!"
    );
  };

  return (
    <>
      <Navbar register={register} />
      <div className="hackathon-image-section">
        <img src="/assets/Banner Layers.png" alt="Upper Image" className="hackathon-image upper" />
      </div>
      <section id="about">
        <About />
        </section>
        
        <section>
        <Waves/>
      </section>
      
      <section id="theme">
        <Theme />
      </section>
      <section id="timelines">
        <Timelines />
      </section>
      <section id="prize">
        <Prize />
      </section>
      <section id="organiser">
        <Organiser />
      </section>
      <section id="faq">
        <FAQ />
      </section>
      <Footer />
    </>
  );
};

export default App;
