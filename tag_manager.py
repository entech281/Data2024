
_tag_manager = None


def get_tag_manager():
    global _tag_manager
    if _tag_manager is None:
        gs = _connect()
        _tag_manager = TeamTagManager(gs)
    return _tag_manager


class TeamTagManager:
    def __init__(self, gs):
        self.spreadsheet = gs
        self.worksheet_tab = gs.worksheet("DCMP_Tags")
        self.tag_list_sheet = gs.worksheet("TeamTags")
        self.fetch()
        self._load_defined_tags()

    def _load_defined_tags(self):
        tag_list_df = get_as_dataframe(self.tag_list_sheet, usecols=[0]).dropna(how='all')
        self.all_tag_list = list(tag_list_df['Tags'])

    def update(self):
        set_with_dataframe(self.worksheet_tab, self.df)
        self.fetch()

    def fetch(self):
        print("Fetching Tag Data")
        tag_list_df = get_as_dataframe(self.worksheet_tab, usecols=[0, 1]).dropna(how='all')
        tag_list_df = tag_list_df.replace(np.NaN, '')

        self.df = tag_list_df
        self.df['team_number'] = self.df['team_number'].apply(int)
        tag_list_df['tag_list'] = tag_list_df['tags'].str.split(",")
        tag_list_df = tag_list_df.explode('tag_list')[['team_number', 'tag_list']]

        self.tag_summary = tag_list_df.groupby('tag_list')['team_number'].apply(list)

    def get_tags_by_team(self):
        return self.df[['team_number', 'tag_list']]

    def get_tags_for_team(self, team_number):
        t = self.df[self.df["team_number"] == team_number]
        if len(t) != 0:
            s = t.iloc[0]['tags']
            if s is not None and len(s) > 0:
                return s.split(',')
        return []

    def update_tags_for_team(self, team_number, tags):
        tags_str = ",".join(tags)

        if len(self.df[self.df['team_number'] == team_number]) == 0:
            new_tags = pd.DataFrame([{'team_number': team_number, 'tags': tags_str}])
            self.df = pd.concat([self.df, new_tags])
        else:
            self.df.loc[self.df['team_number'] == team_number, 'tags'] = tags_str

        df_to_write = self.df[['team_number', 'tags']]
        set_with_dataframe(self.worksheet_tab, df_to_write)
        self.update()
