import requests

job_description = """We Are Hiring | AI Specialist (AI, Automation & Digital Transformation)

Work Location: Dubai Investment Park (DIP) 2, Dubai, UAE

We are looking for a Full Stack Developer with strong AI, automation, functional, and technical knowledge to build and support our in-house software and digital transformation initiatives.
The role will focus on understanding business processes, identifying manual work, developing software solutions, integrating departmental workflows, implementing AI, and continuously improving business operations.

Key Responsibilities

* Develop and maintain in-house business applications.
* Understand departmental workflows and convert manual and Excel-based processes into software automation.
* Work with Joinery, MEP, Manufacturing, Projects, Procurement, Finance, HR, and other departments to identify automation opportunities.
* Develop AI-powered solutions for production planning, scheduling, reporting, estimation, material planning, quality analysis, and workflow optimization.
* Build dashboards, reports, and management information systems to support decision-making.
* Develop an in-house AI chatbot to help employees access information, interact with internal systems, and support business processes.
* Develop an internal task and work management system similar to Jira to assign, track, prioritize, monitor, and report departmental tasks and projects.
* Develop AI-assisted workflows for SOPs, documentation, reports, and operational records.
* Design and develop solutions with a clean, well-structured, and scalable architecture, always considering scalability, performance, efficiency, maintainability, and future business growth.
* Work directly with Department Heads, stakeholders, and the Assistant General Manager to understand business requirements.
* Implement AI, automation, APIs, and emerging technologies to improve business processes.
* Support employees in adopting AI tools and provide AI training and guidance where required.
* Continuously evaluate emerging technologies and implement solutions that provide measurable business value.
* Take ownership of development from requirement gathering, design, development, testing, deployment, and support.
* Server-related activities will be handled by the Headquarters IT & Intelligence Team.
* Ensure fast and efficient development and implementation, without compromising clean architecture, scalability, maintainability, or overall solution quality.


Mandatory Technical Skills

* .NET / C#
* Python
* SQL
* React / Next.js
* REST APIs & API Integration
* AI / LLM / AI API Integration


Requirements

* Minimum 2+ years of Full Stack Software Development experience.
* Strong Functional and Technical knowledge.
* Ability to understand business processes and independently develop practical software solutions.
* Strong interest in AI, automation, and emerging technologies.
* Ability to work with changing requirements and develop flexible solutions.
* Strong analytical and problem-solving skills.
* Ability to work independently while collaborating with the Headquarters IT & Intelligence Team.
* Willingness to learn, experiment, and introduce new technology ideas to the organization.
"""

response = requests.post("http://127.0.0.1:8000/jobs", json={"description": job_description})
print(response.status_code)
print(response.json())