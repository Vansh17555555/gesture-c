import React from 'react'

const Waves = () => {
  return (

      <div className="waves-container">
     
       
          <div className='waves-image'>
            <img src="/assets/Group 6341.png" alt="Image 1" />
          </div>
        
       
    <div className="waves-content-box">
    <h1 className="waves-title">World Audio Visual<br>
    </br> & Entertainment
     Summit (Waves)</h1>
    <p className="waves-description">
    World Audio Visual & Entertainment Summit (WAVES), scheduled for 5th to 9th February 2025, is a key forum for promoting discussions, collaboration, and innovation in the M&E industry. The event will bring together industry leaders, stakeholders and innovators to discuss prospects, challenges, promote global trade and influence the sector’s future.
    </p>
    
    <a href="#" className="waves-button" onClick={(e) => { e.preventDefault(); register(); }}>WAVES 2025</a>
  </div>
  </div>
  )
}

export default Waves
