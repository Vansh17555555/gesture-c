import React from 'react'

const Theme = ({id}) => {
    return (        
          <section className="theme-container" id={id}>
          <h1 className="theme-heading">THEMES</h1>
          <div className='theme-card-container'>
            {/* Healthcare, Fitness, Well-being Theme Card */}
            <div className="theme-card-1">
          
              <div className="theme-content">
                <h3 className="theme-title">Healthcare,<br></br> Fitness, Well-being</h3>
                <p>This theme encompasses the integration of XR technologies into the healthcare sector, focusing on enhancing patient care, promoting fitness, and improving overall well-being.
                </p>
              </div>
            </div>
      
            {/* Educational Transformation Theme Card */}
            <div className="theme-card-2">
             
              <div className="theme-content">
                <h3 className="theme-title">Educational Transformation</h3>
                <p>This theme centers on the potential of XR to revolutionize education and training. Participants will delve into the ways immersive technologies can create engaging learning environments, enhance accessibility, and facilitate experiential learning.</p>
              </div>
            </div>
      
            {/* Immersive Tourism Theme Card */}
            <div className="theme-card-3">
             
              <div className="theme-content">
                <h3 className="theme-title">Immersive Tourism</h3>
                <p>This theme highlights the role of XR in enhancing travel experiences and promoting cultural exchange. Participants will explore how immersive technologies can transform the way people experience destinations, allowing for virtual exploration and interaction with local cultures. 
                </p>
              </div>
            </div>
      
            {/* Digital Media & Entertainment Theme Card */}
            <div className="theme-card-4">
             
              <div className="theme-content">
                <h3 className="theme-title">Digital  Media  &<br></br> Entertainment</h3>
                <p>This theme focuses on the evolving landscape of digital media and entertainment through the lens of XR technologies. Participants will investigate how immersive experiences can redefine storytelling, gaming, and content consumption. </p>
              </div>
            </div>
      
            {/* eCommerce & Retail Transformation Theme Card */}
            <div className="theme-card-5">

              <div className="theme-content">
                <h3 className="theme-title">eCommerce & Retail 
                  <br></br>Transformation</h3>
                <p>This theme explores the transformative impact of XR on retail, eCommerce, and real estate. Participants will examine how immersive technologies can enhance customer experiences, streamline shopping processes, and create personalized environments.</p>
              </div>
            </div>
          </div>
          </section>

      );
      
}

export default Theme
