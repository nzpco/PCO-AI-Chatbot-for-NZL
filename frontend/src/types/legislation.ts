export interface LegislationFragment {
  _id: string;
  chunk_id: string;
  fragment_type: string;
  fragment_label: string | null;
  descriptive_label: string | null;
  heading: string | null;
  text: string;
  summary: string | null;
  summary_long: string | null;
  summary_context: string | null;
  token_count: number;
  act_name: string | null;
  act_number: string | null;
  act_year: string | null;
  schedule_label: string | null;
  schedule_name: string | null;
  part_label: string | null;
  part_name: string | null;
  subpart_label: string | null;
  subpart_name: string | null;
  crosshead_name: string | null;
  section_label: string | null;
  section_name: string | null;
  paragraph_label: string[];
}

export interface RetrievedFragment {
  fragment: LegislationFragment;
  score: number;
}