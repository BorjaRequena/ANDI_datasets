# AUTOGENERATED! DO NOT EDIT! File to edit: source_nbs/models_phenom.ipynb (unless otherwise specified).

__all__ = ['models_phenom', 'models_phenom', 'models_phenom', 'models_phenom', 'models_phenom', 'models_phenom',
           'models_phenom', 'models_phenom', 'models_phenom', 'models_phenom', 'models_phenom', 'models_phenom',
           'models_phenom', 'models_phenom', 'models_phenom']

# Cell
import numpy as np
from stochastic.processes.noise import FractionalGaussianNoise as FGN
import warnings

from .utils_trajectories import gaussian

# Cell
class models_phenom():
    def __init__(self):
        '''Constructor of the class'''
        # We define here the bounds of the anomalous exponent and diffusion coefficient
        self.bound_D = [0, 1e12]
        self.bound_alpha = [0, 1.999]

        # Diffusion state labels: the position of each type defines its numerical label
        # i: immobile/trapped; c: confined; f: free-diffusive (normal and anomalous); d: directed
        self.lab_state = ['i', 'c', 'f', 'd']

# Cell
class models_phenom(models_phenom):

    @staticmethod
    def _single_state_traj(T = 200,
                          D = 1,
                          alpha = 1,
                          L = None,
                          deltaT = 1):

        # Trajectory
        dispx, dispy = FGN(hurst = alpha/2).sample(n = T), FGN(hurst = alpha/2).sample(n = T)
        dispx, dispy = np.sqrt(2*D*deltaT)*(dispx/np.std(dispx)), np.sqrt(2*D*deltaT)*(dispy/np.std(dispy))
        # labels
        labels = np.vstack((np.ones(T)*alpha,
                            np.ones(T)*D,
                            np.ones(T)*models_phenom().lab_state.index('f')
                           )).transpose()

        # If there are no boundaries
        if not L:
            posx, posy = np.cumsum(dispx) - dispx[0], np.cumsum(dispy) - dispy[0]

            return np.vstack((posx, posy)).transpose(), labels

        # If there are, apply reflecting boundary conditions
        else:
            pos = np.zeros((T, 2))

            # Initialize the particle in a random position of the box
            pos[0, :] = np.random.rand(2)*L
            for t in range(1, T):
                pos[t, :] = [pos[t-1, 0]+dispx[t], pos[t-1, 1]+dispy[t]]


                # Reflecting boundary conditions
                while np.max(pos[t, :])>L or np.min(pos[t, :])< 0:
                    pos[t, pos[t, :] > L] = pos[t, pos[t, :] > L] - 2*(pos[t, pos[t, :] > L] - L)
                    pos[t, pos[t, :] < 0] = - pos[t, pos[t, :] < 0]

            return pos, labels

# Cell
class models_phenom(models_phenom):


    def single_state(self,
                     N = 10,
                     T = 200,
                     Ds = [1, 0],
                     alphas = [1, 0],
                     L = None):

        data = np.zeros((T, N, 2))
        labels = np.zeros((T, N, 3))

        for n in range(N):
            alpha_traj = gaussian(alphas, bound = self.bound_alpha)
            D_traj = gaussian(Ds, bound = self.bound_D)
            # Get trajectory from single traj function
            pos, lab = self._single_state_traj(T = T,
                                   D = D_traj,
                                   alpha = alpha_traj,
                                   L = L)
            data[:, n, :] = pos
            labels[:, n, :] = lab

        return data, labels

# Cell
class models_phenom(models_phenom):

    @staticmethod
    def _multiple_state_traj(T = 200,
                    M = np.array([[0.9 , 0.1],[0.1 ,0.9]]),
                    Ds = np.array([1, 0.1]), # Diffusion coefficients of two states
                    alphas = np.array([1, 1]), # Anomalous exponents for two states
                    L = None,
                    deltaT = 1,
                    return_state_num = False # if True, returns the number assigned to the curren state
                            ):

        # transform lists to numpy if needed
        if isinstance(M, list):
            M = np.array(M)
        if isinstance(Ds, list):
            Ds = np.array(Ds)
        if isinstance(alphas, list):
            alphas = np.array(alphas)


        pos = np.zeros((T, 2))
        if L: pos[0,:] = np.random.rand(2)*L

        # Diffusing state of the particle
        state = np.zeros(T).astype(int)
        state[0] = np.random.randint(M.shape[0])

        # Init alphas, Ds
        alphas_t = np.array(alphas[state[0]]).repeat(T)
        Ds_t = np.array(Ds[state[0]]).repeat(T)



        # Trajectory
        dispx, dispy = [FGN(hurst = alphas_t[0]/2).sample(n = T),
                        FGN(hurst = alphas_t[0]/2).sample(n = T)]

        dispx, dispy = [np.sqrt(2*Ds_t[0]*deltaT)*(dispx/np.std(dispx)),
                        np.sqrt(2*Ds_t[0]*deltaT)*(dispy/np.std(dispy)) ]


        for t in range(1, T):

            pos[t, :] = [pos[t-1, 0]+dispx[t], pos[t-1, 1]+dispy[t]]

            # at each time, check new state
            state[t] = np.random.choice(np.arange(M.shape[0]), p = M[state[t-1], :])


            if state[t] != state[t-1]:

                alphas_t[t:] =  np.array(alphas[state[t]]).repeat(T-t)
                Ds_t[t:] = np.array(Ds[state[t]]).repeat(T-t)


                # Recalculate new displacements for next steps
                dispx[t:], dispy[t:] = [FGN(hurst = alphas_t[t]/2).sample(n = T-t),
                                        FGN(hurst = alphas_t[t]/2).sample(n = T-t)]

                if len(dispx[t:]) > 1:
                    dispx[t:], dispy[t:] = [np.sqrt(2*Ds_t[t]*deltaT)*(dispx[t:]/np.std(dispx[t:])),
                                            np.sqrt(2*Ds_t[t]*deltaT)*(dispy[t:]/np.std(dispy[t:]))]
                else:
                    dispx[t:], dispy[t:] = [np.sqrt(2*Ds[state[t]]*deltaT)*np.random.randn(),
                                            np.sqrt(2*Ds[state[t]]*deltaT)*np.random.randn()]


            if L is not None:
                # Reflecting boundary conditions
                while np.max(pos[t, :])>L or np.min(pos[t, :])< 0:
                    pos[t, pos[t, :] > L] = pos[t, pos[t, :] > L] - 2*(pos[t, pos[t, :] > L] - L)
                    pos[t, pos[t, :] < 0] = - pos[t, pos[t, :] < 0]

        if return_state_num:
            return pos, np.array((alphas_t, Ds_t, state)).transpose()
        else:
            return pos, np.array((alphas_t, Ds_t, np.ones(T)*models_phenom().lab_state.index('f'))).transpose()



# Cell
class models_phenom(models_phenom):
    def multi_state(self,
                    N = 10,
                    T = 200,
                    M = np.array([[0.9 , 0.1],[0.1 ,0.9]]),
                    Ds = np.array([[1, 0], [0.1, 0]]),
                    alphas = np.array([[1, 0], [1, 0]]),
                    L = None,
                    return_state_num = False):


        trajs = np.zeros((T, N, 2))
        labels = np.zeros((T, N, 3))

        for n in range(N):

            alphas_traj = []
            Ds_traj = []
            for i in range(M.shape[0]):
                alphas_traj.append(float(gaussian(alphas[i], bound = self.bound_alpha)))
                Ds_traj.append(float(gaussian(Ds[i], bound = self.bound_D)))


            # Get trajectory from single traj function
            traj, lab = self._multiple_state_traj(T = T,
                                             L = L,
                                             M = M,
                                             alphas = alphas_traj,
                                             Ds = Ds_traj,
                                             return_state_num = return_state_num
                                            )

            trajs[:, n, :] = traj
            labels[:, n, :] = lab

        return trajs, labels

# Cell
class models_phenom(models_phenom):
    @staticmethod
    def _get_distance(x):
        M = np.reshape(np.repeat(x[ :, :], x.shape[0], axis = 0), (x.shape[0], x.shape[0], 2))
        Mtrans = M.transpose(1,0,2)
        distance = np.sqrt(np.square(M[:,:, 0]-Mtrans[:,:, 0])
                         + np.square(M[:,:, 1]-Mtrans[:,:, 1]))
        return distance

# Cell
class models_phenom(models_phenom):
    @staticmethod
    def _make_escape(Pu, label, diff_state):

        # if unbinding probability is zero
        if Pu == 0:
            return label, diff_state

        label = label.copy()
        diff_state = diff_state.copy()

        label_dimers = np.unique(label[np.argwhere(diff_state == 1)])

        for l in label_dimers:

            if np.random.rand() < Pu:
                # give new label to escaping particles
                diff_state[label == l] = 0
                label[label == l] = np.max(label)+np.arange(2)+1

        return label, diff_state

# Cell
class models_phenom(models_phenom):
    @staticmethod
    def _make_condensates(Pb, label, diff_state, r, distance, max_label):

        label = label.copy()
        diff_state = diff_state.copy()

        # Keeping track of the ones that will dimerize
        already_dimer = []

        for n, l in enumerate(label):

            # Consider conditions in which particles do not dimerize
            if n in already_dimer or diff_state[n] == 1 or l > max_label:
                continue

            # Extract distances to current particle
            distance_to_current = distance[n,:]
            distance_to_current[n] == 0
            close_particles = np.argwhere((distance_to_current < 2*r) & (distance_to_current > 0)).flatten()

            # Loop over all posible dimerizing candidates
            for chosen in close_particles:

                # Consider conditions in which particles do not dimerize
                if chosen in already_dimer or diff_state[chosen] == 1 or label[chosen] > max_label:
                    continue

                # Draw coin to see if particle dimerizes
                if np.random.rand() < Pb:
                    # Add dimerized particles to the new dimer counter
                    already_dimer.append(chosen)
                    already_dimer.append(n)
                    # Update their diffusive state
                    diff_state[n] = 1
                    diff_state[chosen] = 1

                    # dimerize particles
                    label[chosen] = l

                    # if one particles dimers, not more clustering!
                    break

        return label, diff_state

# Cell
class models_phenom(models_phenom):
    def dimerization(self,
                     N = 10,
                     T = 200,
                     L = 100,
                     r = 1,
                     Pu = 0.1, # Unbinding probability
                     Pb = 0.01, # Binding probability
                     Ds = np.array([[1, 0], [0.1, 0]]), # Diffusion coefficients of two states
                     alphas = np.array([[1, 0], [1, 0]]), # Anomalous exponents for two states
                     deltaT = 1,
                     gamma = False
                     ):

        # transform lists to numpy if needed
        if isinstance(Ds, list):
            Ds = np.array(Ds)
        if isinstance(alphas, list):
            alphas = np.array(alphas)

        # Info to save
        pos = np.zeros((T, N, 2)) # position over time
        label = np.zeros((T, N)).astype(int)
        diff_state = np.zeros((T, N)).astype(int)

        # Init position, labels
        pos[0, :, :] = np.random.rand(N, 2)*L
        label[0, :] = np.arange(pos.shape[1])

        # Init alphas, Ds
        # Calculate alpha/D for each particle in each state
        alphas_N = np.array([gaussian(alphas[0], size = N, bound = self.bound_alpha),
                             gaussian(alphas[1], size = N, bound = self.bound_alpha)])
        Ds_N = np.array([gaussian(Ds[0], size = N, bound = self.bound_D),
                         gaussian(Ds[1], size = N, bound = self.bound_D)])
        # define labels over time by means of state 0
        alphas_t = alphas_N[0,:].repeat(T).reshape(N,T).transpose()
        Ds_t = Ds_N[0,:].repeat(T).reshape(N,T).transpose()

        # initial displacements (all free particles)
        disps = np.zeros((T, N, 2))
        for n in range(N):
            dispx, dispy = [FGN(hurst = alphas_t[0, n]/2).sample(n = T),
                            FGN(hurst = alphas_t[0, n]/2).sample(n = T)]

            disps[:, n, 0] = np.sqrt(2*Ds_t[0, n]*deltaT)*(dispx/np.std(dispx))
            disps[:, n, 1] = np.sqrt(2*Ds_t[0, n]*deltaT)*(dispy/np.std(dispy))


        for t in (range(1, T)):

            # Find max label to account later for escaped
            max_label = np.max(label[t-1, :])

            # Make particles escape
            label[t, :], diff_state[t, :] = self._make_escape(Pu,
                                                              label[t-1, :],
                                                              diff_state[t-1, :])

            lab, diff = label[t, :].copy(), diff_state[t, :].copy()

            # get distance + increasing it for escaped to avoid reclustering
            distance = self._get_distance(pos[t-1, :, :])

            # Merge particles in condensates
            label[t, :], diff_state[t, :] = self._make_condensates(Pb,
                                                                 label[t, :],
                                                                 diff_state[t, :],
                                                                 r, distance, max_label)

            # Find particles which changed state
            label_changed, counts = np.unique(label[t, np.not_equal(diff_state[t-1,:], diff_state[t,:])],
                                              return_counts = True)

            # Calculate new displacements for particles which changed state
            for l, count in zip(label_changed, counts):

                index = int(np.argwhere(label[t,:] == l)[0])
                state = diff_state[t, index]

                # If Ds for both states are given or we go from dimer to single
                if isinstance(gamma, bool) or state == 0:
                    alphas_t[t:, label[t, :] == l] = alphas_N[state, label[t, :] == l].repeat(T-t).reshape(count, T-t).transpose()
                    Ds_t[t:, label[t, :] == l] = Ds_N[state, label[t, :] == l].repeat(T-t).reshape(count, T-t).transpose()
                # if there is gamma, we apply the correction to the diffusive state when creating dimers (see the else)
                else:
                    alphas_t[t:, label[t, :] == l] = alphas_N[state, label[t, :] == l].repeat(T-t).reshape(count, T-t).transpose()
                    # The new D is the mean of the particles dimerizing divided by factor gamma
                    Ds_t[t:, label[t, :] == l] = np.mean(Ds_t[t:, label[t, :] == l])/gamma


                for i in np.argwhere(label[t,:] == l):
                    dispx, dispy = [FGN(hurst = float(alphas_t[t, i])/2).sample(n = T-t),
                                    FGN(hurst = float(alphas_t[t, i])/2).sample(n = T-t)]

                    if len(dispx) > 1:
                        disps[t:, i, 0] = np.sqrt(2*float(Ds_t[t, i])*deltaT)*(dispx/np.std(dispx)).reshape(T-t, 1)
                        disps[t:, i, 1] = np.sqrt(2*float(Ds_t[t, i])*deltaT)*(dispy/np.std(dispy)).reshape(T-t, 1)
                    else:
                        disps[t:, i, 0] = np.sqrt(2*float(Ds_t[t, i])*deltaT)*np.random.randn(1)
                        disps[t:, i, 1] = np.sqrt(2*float(Ds_t[t, i])*deltaT)*np.random.randn(1)

            # Update position
            pos[t, :, :] = pos[t-1,:,:]+disps[t, :, :]
            # Consider boundary conditions
            if L is not None:
                while np.max(pos[t,:, :])>L or np.min(pos[t,:, :])< 0:
                    pos[t, pos[t,:, :] > L] = pos[t, pos[t,:, :] > L] - 2*(pos[t, pos[t,:, :] > L] - L)
                    pos[t, pos[t,:, :] < 0] = - pos[t, pos[t,:, :] < 0]


        return pos, np.array((alphas_t, Ds_t, np.ones_like(alphas_t)*self.lab_state.index('f'))).transpose(1,2,0)


# Cell
class models_phenom(models_phenom):
    @staticmethod
    def _update_bound(mask, # current bind vector
                         N, # number of particles
                         pos, # position of particles
                         Nt, # number of traps
                         traps_pos, # position of traps
                         Pb, # binding probability
                         Pu, # unbinding probability
                         r, # trap radius
                        ):

        # from the ones that are bound, get the ones that unbind. These will be descarted for binding in same time step
        mask_new_free = np.array(1-(np.random.rand(N) < Pu)*mask).astype(bool)

        # calculate the distance between traps and particles
        d = models_phenom._get_distance(np.vstack((traps_pos, pos)))[Nt:, :Nt]
        mask_close = (d < r).sum(1).astype(bool)

        # get mask for binding
        mask_new_bind = np.random.rand(N) < Pb

        # update the bound vector with the previous conditions:
        # first, the ones that unbind
        mask *= mask_new_free
        # then, the ones that are close + bind. Mask_new_free is added to avoid binding
        # of the ones that just unbound
        mask += mask_close*mask_new_bind*mask_new_free

        return mask

# Cell
class models_phenom(models_phenom):

    def immobile_traps(self,
                       N = 10,
                       T = 200,
                       L = 100,
                       r = 1,
                       Pu = 0.1, # Unbinding probability
                       Pb = 0.01, # Binding probability
                       Ds = [1, 0], # Diffusion coefficients of moving state
                       alphas = [1, 0], # Anomalous exponents of moving state
                       Nt = 10,
                       traps_pos = None,
                       deltaT = 1
                      ):

        # Info to output
        pos = np.zeros((T, N, 2)) # position over time
        output_label = np.zeros((T, N, 3))

        disps = np.zeros((T, N, 2))
        diff_state = np.zeros((T, N)).astype(int)
        mask_bound = diff_state[0, :].astype(bool)

        # Init position, labels
        pos[0, :, :] = np.random.rand(N, 2)*L

        # Init alphas, Ds
        # Calculate alpha/D for each particle in state free state
        alphas_N = gaussian(alphas, size = N, bound = self.bound_alpha)
        Ds_N = gaussian(Ds, size = N, bound = self.bound_D)

        # Traps positions
        if traps_pos is None:
            traps_pos = np.random.rand(Nt, 2)*L


        for n in range(N):
            dispx, dispy = [FGN(hurst = alphas_N[n]/2).sample(n = T),
                            FGN(hurst = alphas_N[n]/2).sample(n = T)]

            disps[:, n, 0] = np.sqrt(2*Ds_N[n]*deltaT)*(dispx/np.std(dispx))
            disps[:, n, 1] = np.sqrt(2*Ds_N[n]*deltaT)*(dispy/np.std(dispy))

        # Set initial values of labels
        output_label[0, :, 0] = alphas_N
        output_label[0, :, 1] = Ds_N


        for t in (range(1, T)):

            mask_bound = self._update_bound(mask = mask_bound, # current bind vector
                                         N = N, # number of particles
                                         pos = pos[t-1, :, :], # position of particles
                                         Nt = Nt, # number of traps
                                         traps_pos = traps_pos, # position of traps
                                         Pb = Pb, # binding probability
                                         Pu = Pu, # unbinding probability
                                         r = r, # trap radius
                                         )
            # Update the diffusive state
            diff_state[t,:] = mask_bound

            # Regenerate trajectories for untrapped particles
            untrapped = np.argwhere((diff_state[t,:] - diff_state[t-1,:]) == -1).flatten()
            for un_part in untrapped:
                    if T-t > 1:
                        # Recalculate new displacements for next steps
                        dispx, dispy = [FGN(hurst = alphas_N[un_part]/2).sample(n = T-t),
                                        FGN(hurst = alphas_N[un_part]/2).sample(n = T-t)]

                        disps[t:, un_part, 0] = np.sqrt(2*Ds_N[un_part]*deltaT)*(dispx/np.std(dispx))
                        disps[t:, un_part, 1] = np.sqrt(2*Ds_N[un_part]*deltaT)*(dispy/np.std(dispy))

                    else:
                        disps[t:, un_part, 0] = np.sqrt(2*Ds_N[un_part]*deltaT)*np.random.randn()
                        disps[t:, un_part, 1] = np.sqrt(2*Ds_N[un_part]*deltaT)*np.random.randn()

            # Update the position
            pos[t, :, :] = pos[t-1, :, :] + (1-mask_bound).reshape(N,1)*disps[t, :, :]

            # Update labels
            output_label[t, :, 0] = alphas_N*(1-mask_bound)
            output_label[t, :, 1] = Ds_N*(1-mask_bound)

            # Consider boundary conditions
            if L is not None:
                while np.max(pos[t,:, :])>L or np.min(pos[t,:, :])< 0:
                    pos[t, pos[t,:, :] > L] = pos[t, pos[t,:, :] > L] - 2*(pos[t, pos[t,:, :] > L] - L)
                    pos[t, pos[t,:, :] < 0] = - pos[t, pos[t,:, :] < 0]

        # Define state of particles based on values of Ds and alphas. Here, we use the fact
        # that alpha = 0 for immobilization
        output_label[output_label[:,:,0] == 0, -1] = self.lab_state.index('i')
        output_label[output_label[:,:,0] != 0, -1] = self.lab_state.index('f')

        return pos, output_label

# Cell
class models_phenom(models_phenom):

    @staticmethod
    def _distribute_circular_compartments(Nc, r, L):
        '''Distributes circular compartments over an environment without overlapping. Raises a warning and stops when no more compartments can be inserted.
        Arguments:
        :Nc (float):
            - number of compartments
        :r (float):
            - Size of the compartments
        :L (float):
            - Side length of the squared environment.
        Return:
        :comp_center (numpy.array):
            - Position of the centers of the compartments
           '''

        comp_center = np.random.rand(1, 2)*(L - 2*r) + r
        hardness = 0
        while comp_center.shape[0] < Nc:

            new_pos = np.random.rand(2)*(L - 2*r) + r

            distance = np.linalg.norm(comp_center - new_pos, axis = 1)

            if min(distance) > 2*r:
                comp_center = np.vstack((comp_center, new_pos.reshape(1,2)))

            hardness += 1
            if hardness > Nc*100:
                warn_str = f'Could accomodate {comp_center.shape[0]} circles of the {Nc} requested. Increase size of environment or decrease radius of compartments.'
                warnings.warn(warn_str)
                break

        return comp_center

# Cell
from .utils_trajectories import trigo

class models_phenom(models_phenom):

    @staticmethod
    def _reflected_position(circle_center,
                            circle_radius,
                            beg,
                            end,
                            precision_boundary = 1e-4):

        # If the begining of the segment is in the exact boundary, no intersection is found.
        # In that case, we bring closer the point to the center of the cercle so it is
        # at a distance 'precision_boundary' from the border
        if np.linalg.norm(circle_center - beg) > circle_radius - precision_boundary:
            vec = trigo.seg_to_vec([circle_center, beg])
            beg = np.array(circle_center)+(circle_radius-precision_boundary)*(-np.array(vec)/np.dot(vec, vec)**0.5)

        # find the intersection between the line drawn by the displacement and the circle
        intersect = trigo.circle_line_segment_intersection(circle_center = circle_center,
                                                           circle_radius = circle_radius,
                                                           pt1 = beg,
                                                           pt2 = end)[-1]
        # Draw lines and calculate angles between radius and begining-intersection
        line1 = [circle_center, intersect]
        line2 = [beg, intersect]
        angle = trigo.ang_line(line1, line2)
        # Calculate distance between intersection and end of displacement
        dist_int_end = np.linalg.norm(np.array(intersect) - end)
        # Create radius vector and calculate the tangent vector
        vec_radius = trigo.seg_to_vec([circle_center, intersect])
        tangent = trigo.rotate_vec(vec_radius, np.pi/2)
        # Calculate the angle between the tangent and the displacement vector
        angle_tan = trigo.ang_vec(tangent, trigo.seg_to_vec([beg, intersect]))
        # Change sign to correct get the reflection
        if angle_tan < np.pi/2: angle = - angle
        # Rotate the radius vector with the reflection angle and normalize by magnitude
        vec_bounce = trigo.rotate_vec(vec_radius, angle)
        vec_bounce /= np.dot(vec_bounce, vec_bounce)**0.5
        # Final point is the previous vector times the distance starting at the intersect point
        return np.array(intersect)+dist_int_end*np.array(vec_bounce), intersect

# Cell
class models_phenom(models_phenom):

    @staticmethod
    def _confinement_traj(T = 200,
                          Ds = np.array([1, 0.1]),
                          alphas = np.array([1, 1]),
                          L = 100,
                          deltaT = 1,
                          r = 1,
                          comp_center = None,
                          Nc = 10,
                          trans = 0.1):


        # transform lists to numpy if needed
        if isinstance(Ds, list):
            Ds = np.array(Ds)
        if isinstance(alphas, list):
            alphas = np.array(alphas)

        # Traps positions
        if comp_center is None:
            comp_center = models_phenom._distribute_circular_compartments(Nc = Nc,
                                                                          r = r,
                                                                          L = L)
        # Particle's properties
        pos = np.zeros((T, 2))
        pos[0,:] = np.random.rand(2)*L

        state = np.zeros(T).astype(int)
        # Check if particle is compartment
        distance_centers = np.linalg.norm(comp_center - pos[0, :], axis = 1)
        if distance_centers.min() < r:
            # we assign the state to the compartment the particle is on
            compartment = distance_centers.argmin()
            state[0] = 1

        # Output labels
        labels = np.zeros((T, 3))
        labels[0, 0] = alphas[state[0]]
        labels[0, 1] = Ds[state[0]]



        # Trajectory
        dispx, dispy = FGN(hurst = alphas[state[0]]/2).sample(n = T), FGN(hurst = alphas[state[0]]/2).sample(n = T)
        dispx, dispy = np.sqrt(2*Ds[state[0]]*deltaT)*(dispx/np.std(dispx)), np.sqrt(Ds[state[0]])*(dispy/np.std(dispy))
        disp_t = 0


        for t in range(1, T):
            pos[t, :] = [pos[t-1, 0]+dispx[disp_t], pos[t-1, 1]+dispy[disp_t]]

            # if the particle was inside a compartment
            if state[t-1] == 1:

                # check if it exited of the compartment
                current_distance = np.linalg.norm(comp_center[compartment, :] - pos[t, :])
                if current_distance > r:
                    coin = np.random.rand()
                    # particle escaping
                    if coin < trans:
                        # check that if we entered in a different comparmetn
                        distance_centers = np.linalg.norm(comp_center - pos[t, :], axis = 1)
                        if distance_centers.min() < r:
                            # we assign the state to the compartment the particle is on
                            compartment = distance_centers.argmin()
                            state[t] = 1
                        else: state[t] = 0

                    # particle reflecting
                    else:
                        beg = pos[t-1, :]
                        while current_distance > r:

                            pos[t, :], intersect = models_phenom._reflected_position(circle_center = comp_center[compartment, :],
                                                                                     circle_radius = r,
                                                                                     beg = beg,
                                                                                     end = pos[t, :])
                            beg = intersect
                            distance_beg = np.linalg.norm(comp_center[compartment, :] - beg)
                            current_distance = np.linalg.norm(comp_center[compartment, :] - pos[t,:])
                        state[t] = 1
                # if the particle stayed inside the compartment
                else: state[t] = 1


            # If particle was outside of the compartment
            elif state[t-1] == 0:
                # Check if particle entered a new compartment
                distance_centers = np.linalg.norm(comp_center - pos[t, :], axis = 1)
                if distance_centers.min() < r:
                    # we assign the state to the compartment the particle is on
                    compartment = distance_centers.argmin()
                    state[t] = 1
                # if the particle stayed outside the comparments
                else: state[t] = 0

            # If the state changed
            if state[t] != state[t-1]:
                # Recalculate new displacements for next steps
                dispx, dispy = [FGN(hurst = alphas[state[t]]/2).sample(n = T-t),
                                FGN(hurst = alphas[state[t]]/2).sample(n = T-t)]



                if len(dispx) > 1:
                    dispx, dispy = [np.sqrt(2*Ds[state[t]]*deltaT)*(dispx/np.std(dispx)),
                                    np.sqrt(2*Ds[state[t]]*deltaT)*(dispy/np.std(dispy))]
                else:
                    dispx, dispy = [np.sqrt(2*Ds[state[t]]*deltaT)*np.random.randn(),
                                    np.sqrt(2*Ds[state[t]]*deltaT)*np.random.randn()]
                disp_t = 0
            # If the state did not change:
            else: disp_t += 1

            # Boundary conditions
            if L is not None:
                # Reflecting boundary conditions
                while np.max(pos[t, :])>L or np.min(pos[t, :])< 0:
                    pos[t, pos[t, :] > L] = pos[t, pos[t, :] > L] - 2*(pos[t, pos[t, :] > L] - L)
                    pos[t, pos[t, :] < 0] = - pos[t, pos[t, :] < 0]


            labels[t, 0] = alphas[state[t]]
            labels[t, 1] = Ds[state[t]]

        # Define state of particles based on the state array
        labels[state == 0, -1] = models_phenom().lab_state.index('f')
        labels[state == 1, -1] = models_phenom().lab_state.index('c')

        return pos, labels



# Cell
class models_phenom(models_phenom):
    def confinement(self,
                    N = 10,
                    T = 200,
                    Ds = np.array([[1, 0], [0.1, 0]]),
                    alphas = np.array([[1, 0], [1, 0]]),
                    L = 100,
                    deltaT = 1,
                    r = 1,
                    comp_center = None,
                    Nc = 10,
                    trans = 0.1):

        if isinstance(Ds, list):
            Ds = np.array(Ds)
        if isinstance(alphas, list):
            alphas = np.array(alphas)

        data = np.zeros((T, N, 2))
        labels = np.zeros((T, N, 3))

        for n in range(N):

            # Defined physical parameters for each trajectory
            alphas_traj = []
            Ds_traj = []
            for i in range(Ds.shape[0]):
                alphas_traj.append(gaussian(alphas[i], bound = self.bound_alpha))
                Ds_traj.append(gaussian(Ds[i], bound = self.bound_D))

            # Get trajectory from single traj function
            pos, lab = self._confinement_traj(T = T,
                                              Ds = Ds_traj,
                                              alphas = alphas_traj,
                                              L = L,
                                              deltaT = deltaT,
                                              r = r,
                                              comp_center = comp_center,
                                              Nc = Nc,
                                              trans = trans)
            data[:, n, :] = pos
            labels[:, n, :] = lab

        return data, labels