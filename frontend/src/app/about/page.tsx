export const metadata = {
  title: "About — Expired U.S. Patents | Western University",
  description:
    "Background and purpose of the Western University inactive U.S. patents database.",
};

export default function AboutPage() {
  return (
    <main className="container" style={{ paddingTop: 10, paddingBottom: 40 }}>
      {/* Big back button */}
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
          To find patents that have merely expired you can simply set your search
          terms to look for patents that are 20 years old or older. However,
          finding a list of inactive patents is far more challenging. This website
          overcomes that challenge as it allows you to search through all inactive
          patents in the U.S. that are less than 20 years old. We created this
          database to help drive open source hardware (OSH) development. Patents should be significantly weakened as
          they are actively holding back innovation and technical progress. By
          properly valuing open hardware development it is clear that the return
          on investment for OSH development is enormous. In addition, proactive
          measures to defend the public domain can also provide more safe space
          for innovators to operate. Our hope is that this database accelerates
          your open hardware development.
        </p>


        </div>
    </main>
  );
}