export const metadata = {
  title: "About — Free Inactive Patents II",
  description:
    "Background and purpose of the Free Inactive Patents II database from Western University.",
};

export default function AboutPage() {
  return (
    <main className="container" style={{ paddingTop: 10, paddingBottom: 40 }}>
      <p style={{ margin: "8px 0 18px" }}>
        <a href="/" className="link-btn ghost" aria-label="Back to search">
          ← Back to search
        </a>
      </p>

      <h1 className="section-title">About this Database</h1>
      <p className="section-sub" style={{ marginBottom: 20 }}>
        Why we built this resource and how to use it.
      </p>

      <div style={{ maxWidth: 900, fontSize: 16, lineHeight: 1.6 }}>
        <p>
          To find patents that have merely expired you can simply set your
          search terms to look for patents that are 20 years old or older.
          Finding a list of inactive patents, however, is far more challenging.
          This website overcomes that challenge as it allows you to search
          through all inactive patents in the U.S. that are less than 20 years
          old, and we also have loaded all patents that have expired from age
          (20 years or older). We created this database to help drive open
          source hardware (OSH) development. Our previous work has found that{" "}
          <a
            href="https://www.academia.edu/11677580/The_Case_for_Weaker_Patents"
            target="_blank"
            rel="noreferrer"
          >
            patents should be significantly weakened
          </a>{" "}
          as they are actively retarding innovation and technical progress.
        </p>

        <p>
          There is also very strong evidence that{" "}
          <a
            href="https://ttb.sk/clanky/do-universities-investing-in-technology-transfer-via-patenting-lose-money-joshua-m-pearce/"
            target="_blank"
            rel="noreferrer"
          >
            universities lose money patenting
          </a>
          . By properly{" "}
          <a
            href="https://www.academia.edu/10143203/Quantifying_the_Value_of_Open_Source_Hard_ware_Development"
            target="_blank"
            rel="noreferrer"
          >
            valuing open hardware development
          </a>{" "}
          it is clear that the{" "}
          <a
            href="https://www.academia.edu/13799962/Return_on_Investment_for_Open_Source_Hardware_Development"
            target="_blank"
            rel="noreferrer"
          >
            return on investment for OSH development is enormous
          </a>
          . In addition,{" "}
          <a
            href="https://www.appropedia.org/A_novel_approach_to_obviousness:_An_algorithm_for_identifying_prior_art_concerning_3-D_printing_materials"
            target="_blank"
            rel="noreferrer"
          >
            proactive measures to defend the public domain
          </a>{" "}
          can also provide more safe space for innovators to operate. This is
          important because{" "}
          <a
            href="https://www.mdpi.com/2411-5134/8/6/141"
            target="_blank"
            rel="noreferrer"
          >
            patent parasites
          </a>{" "}
          (non-inventing entities that patent open-source inventions) are on the
          rise. In the worst case scenarios patenting results in{" "}
          <a
            href="https://link.springer.com/article/10.1007/s10728-025-00516-3"
            target="_blank"
            rel="noreferrer"
          >
            withholding innovations that are indirectly responsible for killing
            people
          </a>
          .
        </p>

        <p>
          Our hope is that this database accelerates your open source
          development for the benefit of all humankind.
        </p>

        <p>
          For more information please see the article published in{" "}
          <em>Inventions</em> (2016):{" "}
          <a
            href="https://www.academia.edu/29781601/Open_Source_Database_and_Website_to_Provide_Free_and_Open_Access_to_Inactive_U_S_Patents_in_the_Public_Domain"
            target="_blank"
            rel="noreferrer"
          >
            Open Source Database and Website to Provide Free and Open Access to
            Inactive U.S. Patents in the Public Domain
          </a>
          .
        </p>

        <h2 className="section-title" style={{ fontSize: 22, marginTop: 18 }}>
          About Us
        </h2>

        <p>
          The{" "}
          <a
            href="https://www.appropedia.org/FAST"
            target="_blank"
            rel="noreferrer"
          >
            Free Appropriate Sustainable Technology (FAST)
          </a>{" "}
          research group run by{" "}
          <a
            href="https://www.appropedia.org/User:J.M.Pearce"
            target="_blank"
            rel="noreferrer"
          >
            Professor Joshua Pearce
          </a>
          , at{" "}
          <a href="https://www.uwo.ca/" target="_blank" rel="noreferrer">
            Western University
          </a>{" "}
          in Canada, a top 1% global university. Western is ranked{" "}
          <a
            href="https://www.timeshighereducation.com/rankings/impact/2022/overall"
            target="_blank"
            rel="noreferrer"
          >
            #3 in the world for sustainability
          </a>
          . FAST helps Western achieve its sustainability goals as they explore
          the way{" "}
          <a
            href="https://www.appropedia.org/Photovoltaics"
            target="_blank"
            rel="noreferrer"
          >
            photovoltaic
          </a>{" "}
          technology can sustainably power our society and how{" "}
          <a
            href="https://www.appropedia.org/Category:Open_source_hardware"
            target="_blank"
            rel="noreferrer"
          >
            open-source hardware
          </a>{" "}
          like{" "}
          <a
            href="https://www.appropedia.org/Open_Source_Appropriate_Technology"
            target="_blank"
            rel="noreferrer"
          >
            open source appropriate technologies
          </a>{" "}
          (or OSAT) and{" "}
          <a
            href="https://www.appropedia.org/RepRap"
            target="_blank"
            rel="noreferrer"
          >
            RepRap
          </a>{" "}
          3-D printing can drive distributed recycling and additive
          manufacturing (DRAM) (and maybe even social change).
        </p>

        <p>
          We have a{" "}
          <a
            href="https://www.appropedia.org/FAST_open_access_policy"
            target="_blank"
            rel="noreferrer"
          >
            strong open access policy
          </a>{" "}
          for our own work:
        </p>

        <ul>
          <li>
            <a
              href="https://www.appropedia.org/Category:FAST_methods"
              target="_blank"
              rel="noreferrer"
            >
              FAST methods
            </a>{" "}
            — Exactly how we do what we do (including detailed instructions for
            our open-source 3D printers and scientific equipment) to make your
            own{" "}
            <a
              href="https://www.appropedia.org/Open-source_Lab"
              target="_blank"
              rel="noreferrer"
            >
              open source lab
            </a>
            .
          </li>
          <li>
            <a
              href="https://www.appropedia.org/Category:FAST_literature_reviews"
              target="_blank"
              rel="noreferrer"
            >
              FAST literature reviews
            </a>{" "}
            — For background reading.
          </li>
          <li>
            <a
              href="https://www.appropedia.org/Category:FAST_Completed"
              target="_blank"
              rel="noreferrer"
            >
              FAST Publications By Topic
            </a>
            :{" "}
            <a
              href="https://www.appropedia.org/FAST_Agrivoltaics"
              target="_blank"
              rel="noreferrer"
            >
              Agrivoltaics
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_energy_conservation"
              target="_blank"
              rel="noreferrer"
            >
              Energy Conservation
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_energy_policy_and_sustainability_policy"
              target="_blank"
              rel="noreferrer"
            >
              Energy Policy
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/FAST_floatovoltaics"
              target="_blank"
              rel="noreferrer"
            >
              Floatovoltaics
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_industrial_symbiosis"
              target="_blank"
              rel="noreferrer"
            >
              Industrial Symbiosis
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_life_cycle_analysis_and_net_energy"
              target="_blank"
              rel="noreferrer"
            >
              Life Cycle Analysis
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_materials_science_and_engineering"
              target="_blank"
              rel="noreferrer"
            >
              Materials Science
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_open_source_medical_publications"
              target="_blank"
              rel="noreferrer"
            >
              Medical
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_open_source"
              target="_blank"
              rel="noreferrer"
            >
              Open Source
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_solar_photovoltaic_systems"
              target="_blank"
              rel="noreferrer"
            >
              Photovoltaic Systems
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/FAST_food"
              target="_blank"
              rel="noreferrer"
            >
              Resilient Food
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_solar_photovoltaic_device_physics"
              target="_blank"
              rel="noreferrer"
            >
              Solar Cells
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_sustainable_development_and_open_source_appropriate_technology"
              target="_blank"
              rel="noreferrer"
            >
              Sustainable Development
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_publications_in_education_for_sustainability_and_green_pedagogy"
              target="_blank"
              rel="noreferrer"
            >
              Sustainability Education
            </a>{" "}
            ·{" "}
            <a
              href="https://www.appropedia.org/Pearce_open_source_water_publications"
              target="_blank"
              rel="noreferrer"
            >
              Water
            </a>
          </li>
        </ul>

        <hr style={{ margin: "18px 0" }} />

        <p className="small">
          Source code:&nbsp;
          <a
            href="https://github.com/BilalSaad1/UWO_Patent_Website"
            target="_blank"
            rel="noreferrer"
          >
            BilalSaad1/UWO_Patent_Website
          </a>{" "}
          (GNU General Public License v3.0). Archived at OSF:&nbsp;
          <a
            href="https://osf.io/your-project-id-here"
            target="_blank"
            rel="noreferrer"
          >
            OSF project page
          </a>
          .
        </p>
      </div>
    </main>
  );
}